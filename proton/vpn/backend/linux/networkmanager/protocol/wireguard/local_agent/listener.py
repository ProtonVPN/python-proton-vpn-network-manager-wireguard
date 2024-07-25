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

from proton.vpn.backend.linux.networkmanager.protocol.wireguard.local_agent \
    import AgentConnection, StatusMessage

from proton.vpn import logging

logger = logging.getLogger(__name__)


class AgentListener:
    """Listens for local agent messages."""

    def __init__(self, subscribers: Optional[List[Awaitable]] = None):
        self._subscribers = subscribers or []
        self._background_task = None

    @property
    def background_task(self):
        """Returns the background task that listens for local agent messages."""
        return self._background_task

    def start(self, agent_connection: AgentConnection):
        """Start listening for local agent messages in the background."""
        if self._background_task:
            logger.warning("Local agent listener was already started")
            return

        self._background_task = asyncio.create_task(self.listen(agent_connection))
        self._background_task.add_done_callback(self._on_background_task_stopped)

    async def listen(self, agent_connection: AgentConnection):
        """Listens for local agent messages."""
        logger.info("Starting local agent listener...")
        while True:
            message = await agent_connection.read()
            await self._notify_subscribers(message)

    def _on_background_task_stopped(self, background_task: asyncio.Task):
        self._background_task = None
        logger.info("Local agent listener stopped")
        try:
            # Bubble up any unexpected exceptions.
            background_task.result()
        except asyncio.CancelledError:
            # A cancelled error is expected when the listener is stopped.
            pass

    def stop(self):
        """Stop listening to the local agent connection."""
        if self._background_task:
            self._background_task.cancel()

    async def _notify_subscribers(self, message: StatusMessage):
        """Notify all subscribers of a new message."""
        for subscriber in self._subscribers:
            await subscriber(message)
