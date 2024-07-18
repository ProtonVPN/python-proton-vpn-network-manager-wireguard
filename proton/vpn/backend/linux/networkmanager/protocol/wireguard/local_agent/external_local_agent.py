"""
Local Agent module that uses Proton external local agent implementation.


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

# NOTE: linter warnings have been disabled because project is not yet fully
# deployable to the public, and if any hotfix are required these changes
# might end up in public repos, thus breaking other packages.
# TO-DO: Remove linter warnings once python3-local-agent has been moved to WG Package.
import proton.vpn.local_agent # noqa pylint: disable=import-error, no-name-in-module
from proton.vpn.local_agent import State, LocalAgentError, ExpiredCertificateError # noqa pylint: disable=import-error, no-name-in-module, unused-import
from proton.vpn.session.exceptions import VPNCertificateExpiredError


class AgentConnector:  # pylint: disable=too-few-public-methods
    """AgentConnector that wraps Proton external local agent implementation."""
    async def connect(self, vpn_server_domain: str, credentials):
        """Connect to the local agent server."""
        try:
            certificate = credentials.certificate_pem
        except VPNCertificateExpiredError as exc:
            raise ExpiredCertificateError("Certificate expired") from exc

        return await proton.vpn.local_agent.AgentConnector().connect(  # pylint: disable=E1101
            vpn_server_domain,
            credentials.get_ed25519_sk_pem(),
            certificate
        )
