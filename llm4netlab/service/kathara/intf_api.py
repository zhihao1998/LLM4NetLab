from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


class IntfAPIMixin:
    """
    Interfaces to interact with host interfaces within Kathara.
    """

    def intf_down(self: _SupportsBase, host_name: str, interface: str) -> list[str]:
        """
        Set a specific interface of a host down.
        """
        command = f"ip link set {interface} down"
        return self._run_cmd(host_name, command)

    def intf_up(self: _SupportsBase, host_name: str, interface: str) -> list[str]:
        """
        Set a specific interface of a host up.
        """
        command = f"ip link set {interface} up"
        return self._run_cmd(host_name, command)

    def intf_show(self: _SupportsBase, host_name: str, interface: str) -> list[str]:
        """
        Show the status of a specific interface of a host.
        """
        command = f"ip addr show {interface}"
        return self._run_cmd(host_name, command)


class KatharaIntfAPI(KatharaBaseAPI, IntfAPIMixin):
    """
    Kathara interface API to manage host interfaces.
    """

    pass


if __name__ == "__main__":
    lab_name = "ospf_frr_single_area"
    kathara_api = KatharaIntfAPI(lab_name)
    kathara_api.intf_down("bb0", "eth0")
    print(kathara_api.intf_show("bb0", "eth0"))
    kathara_api.intf_up("bb0", "eth0")
    print(kathara_api.intf_show("bb0", "eth0"))
