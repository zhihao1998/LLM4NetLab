from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


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
    def frr_get_ospf_conf(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Get the OSPF configuration of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf'"
        return self._run_cmd(device_name, command)

    def frr_get_ospf_neighbors(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Get the OSPF neighbors of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf neighbor'"
        return self._run_cmd(device_name, command)

    def frr_get_ospf_routes(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Get the OSPF routes of the FRR instance.
        """
        command = "vtysh -c 'show ip route ospf'"
        return self._run_cmd(device_name, command)

    def frr_get_ospf_interfaces(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Get the OSPF interfaces of the FRR instance.
        """
        command = "vtysh -c 'show ip ospf interface'"
        return self._run_cmd(device_name, command)

    # BGP
    def frr_get_bgp_conf(self: _SupportsBase, device_name: str) -> list[str]:
        """
        Get the BGP configuration of the FRR instance.
        """
        command = "vtysh -c 'show ip bgp'"
        return self._run_cmd(device_name, command)

    def frr_conf(self: _SupportsBase, device_name: str, conf_commands: list[str]) -> list[str]:
        """
        Show the FRR configuration.
        """
        command = 'vtysh -c "conf t"'
        for cmd in conf_commands:
            command += f' -c "{cmd}"'
        command += ' -c "end" -c "write"'
        return self._run_cmd(device_name, command)

    def frr_add_route(self: _SupportsBase, device_name: str, route: str, next_hop: str) -> list[str]:
        """
        Add a static route to the FRR instance.
        """
        command = f'vtysh -c "conf t" -c "ip route {route} {next_hop}" -c "end" -c "write"'
        return self._run_cmd(device_name, command)

    def frr_del_route(self: _SupportsBase, device_name: str, route: str, next_hop: str) -> list[str]:
        """
        Delete a static route from the FRR instance.
        """
        command = f'vtysh -c "conf t" -c "no ip route {route} {next_hop}" -c "end" -c "write"'
        return self._run_cmd(device_name, command)

    def frr_add_bgp_advertisement(self: _SupportsBase, device_name: str, network: str, as_path: str) -> list[str]:
        """
        Add a BGP network advertisement to the FRR instance.
        """
        command = f'vtysh -c "conf t" -c "router bgp {as_path}" -c "network {network}" -c "end" -c "write"'
        return self._run_cmd(device_name, command)

    def frr_del_bgp_advertisement(self: _SupportsBase, device_name: str, network: str, as_path: str) -> list[str]:
        """
        Delete a BGP network advertisement from the FRR instance.
        """
        command = f'vtysh -c "conf t" -c "router bgp {as_path}" -c "no network {network}" -c "end" -c "write"'
        return self._run_cmd(device_name, command)


class KatharaFRRAPI(KatharaBaseAPI, IntfAPIMixin):
    pass


if __name__ == "__main__":
    lab_name = "simple_bgp"
    kathara_api = KatharaFRRAPI(lab_name)
    # print(kathara_api.frr_get_ospf_conf("bb0"))
    # print(kathara_api.frr_show_route("bb0"))
    # print(kathara_api.frr_show_ospf_route("bb1"))
    # print(kathara_api.frr_show_ospf_neighbors("bb2"))
    # print(kathara_api.frr_show_ospf_interfaces("bb3"))
    # print(kathara_api.frr_show_ospf_database("bb4"))
    # print(kathara_api.frr_show_ospf_database_router("bb0"))
    # print(kathara_api.frr_show_bgp_conf("router1"))
    # print(kathara_api.frr_conf("router1", ["router bgp 1", "bgp router-id 0.0.0.1"]))
    print(kathara_api.frr_get_bgp_conf("router1"))
