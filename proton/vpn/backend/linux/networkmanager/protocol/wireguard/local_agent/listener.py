"""
Copyright (c) 2024 Proton AG

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
from typing import Optional, List, Awaitable

import proton.vpn.backend.linux.networkmanager.protocol.wireguard.local_agent\
    .fallback_local_agent as fallback_local_agent  # pylint: disable=R0402

from proton.vpn.backend.linux.networkmanager.protocol.wireguard.local_agent \
    import AgentConnection, Status, State, AgentConnector, \
    LocalAgentError, ExpiredCertificateError, Reason, ReasonCode

from proton.vpn import logging

logger = logging.getLogger(__name__)


class AgentListener:
    """Listens for local agent messages."""

    def __init__(
            self, subscribers: Optional[List[Awaitable]] = None,
            connector: Optional[AgentConnector] = None
    ):
        self._subscribers = subscribers or []
        self._connector = connector or AgentConnector()
        self._background_task = None
        self._connection_retries = None

    @property
    def is_running(self):
        """Returns whether the listener is running."""
        return bool(self._background_task)

    @property
    def background_task(self):
        """Returns the background task that listens for local agent messages."""
        return self._background_task

    def start(self, domain: str, credentials: str):
        """Start listening for local agent messages in the background."""
        if self._background_task:
            logger.warning("Agent listener was already started")
            return

        logger.info("Starting agent listener...")
        self._connection_retries = 0
        self._background_task = asyncio.create_task(self._run_in_background(domain, credentials))
        self._background_task.add_done_callback(self._on_background_task_stopped)

    async def _run_in_background(self, domain, credentials):
        """Run the listener in the background."""
        logger.info("Establishing agent connection...")
        connection = await self._connect(domain, credentials)
        logger.info("Agent connection established.")

        if not connection:
            # The fallback local agent implementation does not return a connection object.
            # This branch should be removed after removing the fallback implementation.
            await self._notify_subscribers(fallback_local_agent.Status(state=State.CONNECTED))
            return

        await self.listen(connection)

    async def _connect(self, domain, credentials) -> AgentConnection:
        try:
            return await self._connector.connect(domain, credentials)
        except ExpiredCertificateError:
            logger.exception("Expired certificate upon establishing agent connection.")
            message = fallback_local_agent.Status(
                state=State.HARDJAILED, reason=Reason(code=ReasonCode.CERTIFICATE_EXPIRED)
            )
            await self._notify_subscribers(message)
            raise
        except (TimeoutError, LocalAgentError):
            message = fallback_local_agent.Status(state=State.DISCONNECTED)
            await self._notify_subscribers(message)
            raise

    async def listen(self, agent_connection: AgentConnection):
        """Listens for local agent messages."""
        while True:
            try:
                message = await agent_connection.read()
            except LocalAgentError:
                # Since currently we are raising exceptions when the local agent sends an error
                # response, for now we just log them until we put proper error handling in place.
                logger.exception("Unhandled agent connection error.")
                continue
            except TimeoutError:
                await self._notify_subscribers(
                    fallback_local_agent.Status(state=State.DISCONNECTED)
                )
                raise
            await self._notify_subscribers(message)

    def _on_background_task_stopped(self, background_task: asyncio.Task):
        self._background_task = None
        try:
            # Bubble up any unexpected exceptions.
            background_task.result()
        except asyncio.CancelledError:
            # When the listener is stopped, the background task is cancelled,
            # and it raises this exception.
            logger.info("Agent listener was successfully stopped.")
        except TimeoutError:
            logger.warning("Agent listener timed out.")
        except Exception:
            logger.error("Agent listener was unexpectedly closed.")
            raise

    def stop(self):
        """Stop listening to the local agent connection."""
        if self._background_task:
            self._background_task.cancel()
            self._background_task = None

    async def _notify_subscribers(self, message: Status):
        """Notify all subscribers of a new message."""
        for subscriber in self._subscribers:
            await subscriber(message)
