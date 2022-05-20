import socket

import gi
gi.require_version("NM", "1.0")
from gi.repository import NM

from proton.vpn.backend.linux.networkmanager.core import LinuxNetworkManager


class Wireguard(LinuxNetworkManager):
    """Creates a Wireguard connection."""
    protocol = "wireguard"
    virtual_device_name = "proton0"

    @classmethod
    def _get_priority(cls):
        return 1

    @classmethod
    def _validate(cls):
        # FIX ME: This should do a validation to ensure that NM can be used
        return True

    def __generate_unique_id(self):
        import uuid
        self._unique_id = str(uuid.uuid4())

    def __configure_connection(self):
        new_connection = NM.SimpleConnection.new()

        s_con = NM.SettingConnection.new()
        s_con.set_property(NM.SETTING_CONNECTION_ID, self._get_servername())
        s_con.set_property(NM.SETTING_CONNECTION_UUID, self._unique_id)
        s_con.set_property(NM.SETTING_CONNECTION_TYPE, "wireguard")
        s_con.set_property(NM.SETTING_CONNECTION_INTERFACE_NAME, Wireguard.virtual_device_name)

        s_ipv4 = NM.SettingIP4Config.new()
        s_ipv4.set_property(NM.SETTING_IP_CONFIG_METHOD, "manual")
        s_ipv4.add_address(NM.IPAddress.new(socket.AF_INET, "10.2.0.2", 32))
        s_ipv4.add_dns("10.2.0.1")
        s_ipv4.add_dns_search("~")

        peer = NM.WireGuardPeer.new()
        peer.append_allowed_ip("0.0.0.0/0", False)
        peer.set_endpoint(f"{self._vpnserver.server_ip}:{self._vpnserver.udp_ports[0]}", False)
        peer.set_public_key(self._vpnserver.wg_public_key_x25519, False)

        s_wg = NM.SettingWireGuard.new()
        s_wg.append_peer(peer)
        s_wg.set_property(NM.SETTING_WIREGUARD_PRIVATE_KEY,self._vpncredentials.pubkey_credentials.wg_private_key)

        new_connection.add_setting(s_con)
        new_connection.add_setting(s_ipv4)
        new_connection.add_setting(s_wg)

        self.connection = new_connection
        return

    def __setup_wg_connection(self):
        self.__generate_unique_id()
        self.__configure_connection()
        self.nm_client._add_connection_async(self.connection)

    def _setup(self):
        self.__setup_wg_connection()
