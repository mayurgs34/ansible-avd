from __future__ import annotations

from functools import cached_property
from ipaddress import ip_interface

from ansible_collections.arista.avd.plugins.plugin_utils.utils import get

from .utils import UtilsMixin


class CvxMixin(UtilsMixin):
    """
    Mixin Class used to generate structured config for one key.
    Class should only be used as Mixin to a AvdStructuredConfig class
    """

    @cached_property
    def cvx(self) -> dict | None:
        """
        Detect if this is a CVX server for overlay and configure service & peer hosts accordingly.
        """
        if not (self._overlay_cvx):
            return None

        overlay_cvx_servers = get(self._hostvars, "overlay_cvx_servers", default=[])
        if self._hostname not in overlay_cvx_servers:
            return None

        peer_hosts = []
        for overlay_cvx_server in overlay_cvx_servers:
            if overlay_cvx_server == self._hostname:
                continue

            peer_switch_facts = self._get_peer_facts(overlay_cvx_server, True)
            cvx_server_ip = get(peer_switch_facts, "mgmt_ip", required=True, org_key=f"'mgmt_ip' for CVX Server {overlay_cvx_server}")
            peer_hosts.append(str(ip_interface(cvx_server_ip).ip))

        return {
            "shutdown": False,
            "peer_hosts": peer_hosts,
            "services": {
                "vxlan": {
                    "shutdown": False,
                },
            },
        }
