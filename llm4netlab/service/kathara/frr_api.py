from llm4netlab.service.kathara.base import KatharaBaseAPI, _SupportsBase


class IntfAPIMixin:
    """
    Interfaces to interact with Linux Traffic within Kathara.
    """

    def frr_show_route(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Show the routing table of the FRR instance.
        """
        command = "vtysh -c 'show ip route'"
        return self._run_cmd(device_name, command)

    # OSPF related commands
    def frr_show_ospf_route(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Show the routing table of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf route'"
        return self._run_cmd(device_name, command)

    def frr_show_ospf_neighbors(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Show the OSPF neighbors of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf neighbor'"
        return self._run_cmd(device_name, command)

    def frr_show_ospf_interfaces(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Show the OSPF interfaces of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf interface'"
        return self._run_cmd(device_name, command)

    def frr_show_ospf_database(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Show the OSPF database of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf database'"
        return self._run_cmd(device_name, command)

    def frr_show_ospf_database_router(self: _SupportsBase, device_name: str, router_id: str = "") -> list[str]:
        """
        Show the OSPF database of router links in the FRR instance.
        """
        command = f"vtysh -c 'show ip ospf database router {router_id}'"
        return self._run_cmd(device_name, command)


class KatharaFRRAPI(KatharaBaseAPI, IntfAPIMixin):
    pass


if __name__ == "__main__":
    lab_name = "ospf_frr_single_area"
    kathara_api = KatharaFRRAPI(lab_name)
    print(kathara_api.frr_show_route("bb0"))
    print(kathara_api.frr_show_ospf_route("bb1"))
    print(kathara_api.frr_show_ospf_neighbors("bb2"))
    print(kathara_api.frr_show_ospf_interfaces("bb3"))
    print(kathara_api.frr_show_ospf_database("bb4"))
    print(kathara_api.frr_show_ospf_database_router("bb0"))
