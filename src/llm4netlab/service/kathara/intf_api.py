from typing import Literal

from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


class IntfAPIMixin:
    """
    Interfaces to interact with host interfaces within Kathara.
    """

    def intf_on_off(self: _SupportsBase, host_name: str, interface: str, state: Literal["up", "down"]) -> list[str]:
        """
        Set a specific interface of a host on or off.
        """
        command = f"ip link set {interface} {state}"
        return self.exec_cmd(host_name, command)

    def intf_show(self: _SupportsBase, host_name: str, interface: str) -> list[str]:
        """
        Show the status of a specific interface of a host.
        """
        command = f"ip addr show {interface}"
        return self.exec_cmd(host_name, command)


class KatharaIntfAPI(KatharaBaseAPI, IntfAPIMixin):
    """
    Kathara interface API to manage host interfaces.
    """

    pass


if __name__ == "__main__":
    lab_name = "ospf_frr_single_area"
    kathara_api = KatharaIntfAPI(lab_name)
    kathara_api.intf_on_off("bb0", "eth0", "down")
    print(kathara_api.intf_show("bb0", "eth0"))
    kathara_api.intf_on_off("bb0", "eth0", "up")
    print(kathara_api.intf_show("bb0", "eth0"))
