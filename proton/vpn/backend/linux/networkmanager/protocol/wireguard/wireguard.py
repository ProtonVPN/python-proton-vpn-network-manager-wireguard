"""
This module contains the backends implementing the supported OpenVPN protocols.


Copyright (c) 2023 Proton AG

This file is part of Proton VPN.

Proton VPN is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Proton VPN is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ProtonVPN.  If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio
import socket
import uuid
import logging
from getpass import getuser
from concurrent.futures import Future

import gi
gi.require_version("NM", "1.0")  # noqa: required before importing NM module
# pylint: disable=wrong-import-position
from gi.repository import NM

from proton.vpn.connection.events import EventContext
from proton.vpn.connection import events
from proton.vpn.backend.linux.networkmanager.core import LinuxNetworkManager
from .local_agent import AgentConnector, State, LocalAgentError

logger = logging.getLogger(__name__)


class Wireguard(LinuxNetworkManager):
    """Creates a Wireguard connection."""
    SIGNAL_NAME = "state-changed"
    ADDRESS = "10.2.0.2"
    ADDRESS_PREFIX = 32
    DNS_IP = "10.2.0.1"
    DNS_SEARCH = "~"
    ALLOWED_IP = "0.0.0.0/0"
    DNS_PRIORITY = -1500
    VIRTUAL_DEVICE_NAME = "proton0"
    protocol = "wireguard"
    ui_protocol = "WireGuard (experimental)"
    connection = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connection_settings = None
        self._agent_connection = None

    def setup(self) -> Future:
        """Methods that creates and applies any necessary changes to the connection."""
        self._generate_connection()
        self._modify_connection()
        return self.nm_client.add_connection_async(self.connection)

    def _generate_connection(self):
        self._unique_id = str(uuid.uuid4())
        self._connection_settings = NM.SettingConnection.new()
        self.connection = NM.SimpleConnection.new()

    async def update_credentials(self, credentials):
        """Notifies the vpn server that the wireguard certificate needs a refresh."""
        await super().update_credentials(credentials)
        await self._start_local_agent_connection()

    def _modify_connection(self):
        self._set_custom_connection_id()
        self._set_uuid()
        self._set_interface_name()
        self._set_connection_type()
        self._set_connection_user_owned()
        self.connection.add_setting(self._connection_settings)

        self._set_route()
        self._set_dns()
        self._set_wireguard_properties()

        self.connection.verify()

    def _set_custom_connection_id(self):
        self._connection_settings.set_property(NM.SETTING_CONNECTION_ID, self._get_servername())

    def _set_uuid(self):
        self._connection_settings.set_property(NM.SETTING_CONNECTION_UUID, self._unique_id)

    def _set_interface_name(self):
        self._connection_settings.set_property(
            NM.SETTING_CONNECTION_INTERFACE_NAME, self.VIRTUAL_DEVICE_NAME
        )

    def _set_connection_type(self):
        self._connection_settings.set_property(NM.SETTING_CONNECTION_TYPE, "wireguard")

    def _set_connection_user_owned(self):
        self._connection_settings.add_permission(
            "user",
            getuser(),
            None
        )

    def _set_route(self):
        ipv4_config = NM.SettingIP4Config.new()
        ipv6_config = NM.SettingIP6Config.new()

        ipv4_config.set_property(NM.SETTING_IP_CONFIG_METHOD, "manual")
        ipv4_config.add_address(
            NM.IPAddress.new(socket.AF_INET, self.ADDRESS, self.ADDRESS_PREFIX)
        )

        ipv6_config.set_property(NM.SETTING_IP_CONFIG_METHOD, "disabled")

        self.connection.add_setting(ipv4_config)
        self.connection.add_setting(ipv6_config)

    def _set_dns(self):
        ipv4_config = self.connection.get_setting_ip4_config()
        ipv6_config = self.connection.get_setting_ip6_config()

        ipv4_config.set_property(NM.SETTING_IP_CONFIG_DNS_PRIORITY, self.DNS_PRIORITY)
        ipv6_config.set_property(NM.SETTING_IP_CONFIG_DNS_PRIORITY, self.DNS_PRIORITY)

        ipv4_config.set_property(NM.SETTING_IP_CONFIG_IGNORE_AUTO_DNS, True)
        ipv6_config.set_property(NM.SETTING_IP_CONFIG_IGNORE_AUTO_DNS, True)

        if self._settings.dns_custom_ips:
            ipv4_config.set_property(NM.SETTING_IP_CONFIG_DNS, self._settings.dns_custom_ips)
        else:
            ipv4_config.add_dns(self.DNS_IP)
            ipv4_config.add_dns_search(self.DNS_SEARCH)

        self.connection.add_setting(ipv4_config)
        self.connection.add_setting(ipv6_config)

    def _set_wireguard_properties(self):
        peer = NM.WireGuardPeer.new()
        peer.append_allowed_ip(self.ALLOWED_IP, False)
        peer.set_endpoint(
            f"{self._vpnserver.server_ip}:{self._vpnserver.wireguard_ports.udp[0]}",
            False
        )
        peer.set_public_key(self._vpnserver.x25519pk, False)

        # Ensures that the configurations are valid
        # https://lazka.github.io/pgi-docs/index.html#NM-1.0/classes/WireGuardPeer.html#NM.WireGuardPeer.is_valid
        peer.is_valid(True, True)

        wireguard_config = NM.SettingWireGuard.new()
        wireguard_config.append_peer(peer)
        wireguard_config.set_property(
            NM.SETTING_WIREGUARD_PRIVATE_KEY,
            self._vpncredentials.pubkey_credentials.wg_private_key
        )

        self.connection.add_setting(wireguard_config)

    async def _start_local_agent_connection(self):
        status = None
        try:
            # Close the connection if one already exists
            if self._agent_connection:
                logger.info("Closing existing local agent connection...")
                await self._agent_connection.close()

            # Re-make it
            logger.info("Establishing local agent connection...")
            self._agent_connection = await AgentConnector().connect(
                self._vpnserver.domain,
                self._vpncredentials.pubkey_credentials
            )

            # Query the status to ensure we are correctly connected to the vpn
            logger.info("Getting local agent status...")
            status = await self._agent_connection.get_status()
        except LocalAgentError:
            logger.exception("Error getting local agent status.")

        if status == State.Connected:
            self._notify_subscribers(events.Connected(EventContext(connection=self)))
        else:
            self._notify_subscribers(
                events.UnexpectedError(EventContext(connection=self)))

    # pylint: disable=arguments-renamed
    def _on_state_changed(
            self, _: NM.ActiveConnection, state: int, reason: int
    ):
        """
            When the connection state changes, NM emits a signal with the state and
            reason for the change. This callback will receive these updates
            and translate for them accordingly for the state machine,
            as the state machine is backend agnostic.

            :param state: connection state update
            :type state: int
            :param reason: the reason for the state update
            :type reason: int
        """
        state = NM.ActiveConnectionState(state)
        reason = NM.ActiveConnectionStateReason(reason)

        logger.debug(
            "Wireguard connection state changed: state=%s, reason=%s",
            state.value_name, reason.value_name
        )

        if state is NM.ActiveConnectionState.ACTIVATED:
            future = asyncio.run_coroutine_threadsafe(
                self._start_local_agent_connection(), self._asyncio_loop
            )
            future.add_done_callback(lambda f: f.result())  # Bubble up unhandled exceptions.
        elif state == NM.ActiveConnectionState.DEACTIVATED:
            if reason in [NM.ActiveConnectionStateReason.USER_DISCONNECTED]:
                self._notify_subscribers_threadsafe(
                    events.Disconnected(EventContext(connection=self, error=reason))
                )
            elif reason is NM.ActiveConnectionStateReason.DEVICE_DISCONNECTED:
                self._notify_subscribers_threadsafe(
                    events.DeviceDisconnected(EventContext(connection=self, error=reason))
                )
        else:
            logger.debug("Ignoring VPN state change: %s", state.value_name)

    @classmethod
    def _get_priority(cls):
        return 1

    @classmethod
    def _validate(cls):
        # FIX ME: This should do a validation to ensure that NM can be used
        return True
