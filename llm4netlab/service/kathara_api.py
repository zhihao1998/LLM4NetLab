import asyncio
import json
import re
from typing import Dict, List

from Kathara.manager.docker.stats.DockerLinkStats import DockerLinkStats
from Kathara.manager.Kathara import Kathara
from Kathara.model.Machine import Machine


def _build_thrift_command(api_calls: list[str]) -> str:
    """
    Build a bash command to execute multiple Thrift API calls on the switch.
    Each item in `api_calls` should be a valid method call string,
    e.g., "get_tables()", "get_registers('my_reg')"

    Note: use double quotes for the method calls to avoid escaping issues!
    """
    python_lines = [
        "from sswitch_thrift_API import SimpleSwitchThriftAPI",
        "simple_switch = SimpleSwitchThriftAPI(thrift_port=9090)",
    ]

    for call in api_calls:
        python_lines.append(f"print(simple_switch.{call})")

    python_script = "\n".join(python_lines)

    command = f"bash -c 'cd /usr/local/lib/python3.11/site-packages && python3 << EOF\n{python_script}\nEOF'"
    return command


def _quote_list_double(items: List[str]) -> str:
    """Turn a list of strings into a double-quoted string representation."""
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


class KatharaAPI:
    """
    Interfaces to interact with the Kathara.
    """

    def __init__(self, lab_name: str):
        self.instance = Kathara.get_instance()
        self.lab = self.instance.get_lab_from_api(lab_name=lab_name)
        if self.lab is None:
            raise ValueError(f"Lab {lab_name} not found.")

    def get_mahines(self) -> list[str]:
        """
        Get the list of machines in the lab.
        """
        return self.lab.machines

    def get_hosts(self) -> list[Machine]:
        """
        Get the list of hosts in the lab.
        # TODO: Find better way to get the host names
        """
        return [machine for name, machine in self.lab.machines.items() if machine.name.startswith("pc")]

    def get_switches(self) -> list[Machine]:
        """
        Get the list of switches in the lab.
        """
        return [machine for name, machine in self.lab.machines.items() if machine.name.startswith("s")]

    def get_host_ip(self, host_name: str) -> str:
        """
        Get the IP address of a host.
        """
        result = self._run_cmd(host_name, "ip addr")
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b"

        ips = []
        if isinstance(result, list):
            lines = "\n".join(result).splitlines()
        else:
            lines = result.splitlines()

        for line in lines:
            ips += re.findall(ip_pattern, line)
        ips = [ip.split("/")[0] for ip in ips]
        for ip in ips:
            if not ip.startswith("127."):
                return ip

    def get_links(self) -> dict:
        """
        Get the links of the network.
        """
        links: Dict[str:DockerLinkStats] = next(self.instance.get_links_stats())
        result = {}
        for _, link in links.items():
            if link.name:
                result[link.name] = (link.containers[0].labels["name"], link.containers[1].labels["name"])
        return result

    def get_connectivity(self) -> dict:
        """
        Get the connectivity of the network.
        TODO: need to add which port connects to which host/switch/router.

        Example output:
        {"s1": ["s2", "h1"], "h1": ["s1"], "s2": ["s1"]}
        """
        links = self.get_links()
        links = dict(sorted(links.items(), key=lambda item: item[0]))  # sort by link name
        result = {}
        for _, link in links.items():
            src, dst = link
            result.setdefault(src, []).append(dst)
            result.setdefault(dst, []).append(src)
        return json.dumps(result)

    def _run_cmd(self, machine_name: str, command: str) -> list[str]:
        """
        Run a command on a machine and return its output as a list of strings,
        decoding bytes and filtering out None, empty strings, and zeros.
        """
        output_generator = self.instance.exec(
            machine_name=machine_name, command=command, lab_name=self.lab.name, stream=False
        )

        result = []
        for item in output_generator:
            if not item or item == b"" or isinstance(item, int) or item is None or item == "None":
                continue
            if isinstance(item, bytes):
                item = item.decode("utf-8", errors="ignore").strip()
            elif isinstance(item, str):
                item = item.strip()
            else:
                item = str(item).strip()
            if item:
                result.append(item)

        if isinstance(result, list):
            result = json.dumps(result)
        return result

    # asynchronous
    async def _run_cmd_async(self, machine_name: str, command: str) -> list[str]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._run_cmd, machine_name, command)

    # synchronous version of get_reachability, now deprecated
    # def _check_ping_success(self, host: str, dst_ip: str) -> bool:
    #     """
    #     Check if ping to dst_ip from host is successful.
    #     """
    #     command = f"ping -c 10 {dst_ip}"
    #     result = self._run_cmd(host, command)
    #     matches = re.findall(r"\d+ packets transmitted, \d+ received, .*? packet loss, time \d+ms", result)
    #     if len(matches) > 0:
    #         return matches[0]
    #     else:
    #         return f"Ping command failed on {host} for {dst_ip}. Result: {result}"
    # return any(" 0% packet loss" in line for line in lines)

    # def get_reachability(self) -> dict:
    #     """
    #     Check the reachability of all hosts.
    #     """
    #     # only get hosts without switch, router, or other devices
    #     host_names = sorted([host.name for host in self.get_hosts()])
    #     host_ips = {host_name: self.get_host_ip(host_name) for host_name in host_names}
    #     ping_pairs = []
    #     for index, host_name_i in enumerate(host_names):
    #         for host_name_j in host_names[index + 1 :]:
    #             if host_name_i == host_name_j:
    #                 continue
    #             host_ip_j = host_ips[host_name_j]
    #             ping_pairs.append((host_name_i, host_name_j, host_ip_j))

    #     result = []
    #     for host_name_i, host_name_j, host_ip_j in ping_pairs:
    #         is_ping_success = self._check_ping_success(host_name_i, host_ip_j)
    #         result.append(f"{host_name_i} ping {host_name_j}: {is_ping_success}")
    #         # result.setdefault(f"{host_ip_i}", {}).update(is_ping_success})
    #         # if is_ping_success:
    #         #     result.setdefault(host_name_i, {}).update({host_name_j: "ping success"})
    #         # else:
    #         #     result.setdefault(host_name_i, {}).update({host_name_j: "ping failed"})
    #     return str(result)

    async def _check_ping_success_async(self, host: str, dst_ip: str) -> bool:
        command = f"ping -c 10 {dst_ip}"
        result = await self._run_cmd_async(host, command)
        matches = re.findall(r"\d+ packets transmitted, \d+ received, .*? packet loss, time \d+ms", result)
        if len(matches) > 0:
            return matches[0]
        else:
            return result

    async def get_reachability(self) -> str:
        return await self._get_reachability_async()

    async def _get_reachability_async(self) -> str:
        host_names = [host.name for host in self.get_hosts()]
        host_ips = {host_name: self.get_host_ip(host_name) for host_name in host_names}
        result = []

        coroutines = []
        labels = []

        for host_name_i, host_ip_i in host_ips.items():
            for host_name_j, host_ip_j in host_ips.items():
                if host_name_i == host_name_j:
                    continue
                labels.append((host_name_i, host_name_j))
                coroutines.append(self._check_ping_success_async(host_name_i, host_ip_j))

        responses = await asyncio.gather(*coroutines)
        for (host_i, host_j), is_success in zip(labels, responses):
            result.append(f"{host_i} ping {host_j}: {is_success}")
        return str(result)

    """Log related API"""

    def bmv2_get_log(self, switch_name: str, rows: int = 100) -> list[str]:
        """
        Get the log file of a switch.
        """
        command = f"tail -n {rows} sw.log"
        return self._run_cmd(switch_name, command)

    """ API related to bmv2, invoking the thrift API """

    # Switch related API
    def bmv2_switch_info(self, switch_name: str) -> list[str]:
        """
        Show the switch info.
        """
        command = _build_thrift_command(["show_switch_info()"])
        return self._run_cmd(switch_name, command)

    def bmv2_show_ports(self, switch_name: str) -> list[str]:
        """
        Show the ports of a switch.
        """
        command = _build_thrift_command(["show_ports()"])
        return self._run_cmd(switch_name, command)

    def bmv2_show_tables(self, switch_name: str) -> list[str]:
        """
        Show the tables of a switch.
        """
        command = _build_thrift_command(["show_tables()"])
        return self._run_cmd(switch_name, command)

    def bmv2_show_actions(self, switch_name: str) -> list[str]:
        """
        Show all actions of a switch.
        """
        command = _build_thrift_command(["show_actions()"])
        return self._run_cmd(switch_name, command)

    def bmv2_get_register_arrays(self, switch_name: str) -> list[str]:
        """
        Show all register_arrays of a switch.
        """
        command = _build_thrift_command(["get_register_arrays()"])
        return self._run_cmd(switch_name, command)

    # Table related API
    def bmv2_table_info(self, switch_name: str, table_name: str) -> list[str]:
        """
        Show the info of a table.
        """
        command = _build_thrift_command([f'table_info("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_dump(self, switch_name: str, table_name: str) -> list[str]:
        """
        Dump the content of a table.
        """
        command = _build_thrift_command([f'table_dump("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_show_actions(self, switch_name: str, table_name: str) -> list[str]:
        """
        Show the actions of a table.
        """
        command = _build_thrift_command([f'table_show_actions("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_num_entries(self, switch_name: str, table_name: str) -> list[str]:
        """
        Show the number of entries in a table.
        """
        command = _build_thrift_command([f'table_num_entries("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_clear(self, switch_name: str, table_name: str) -> list[str]:
        """
        Clear the content of a table.
        """
        command = _build_thrift_command([f'table_clear("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_add(
        self,
        switch_name: str,
        table_name: str,
        action_name: str,
        match_keys: List[str],
        action_params: List[str] = [],
        prio: int = 0,
    ) -> list[str]:
        """
        Add an entry to a table.
        """
        match_keys_str = _quote_list_double(match_keys)
        action_params_str = _quote_list_double(action_params)

        command = _build_thrift_command(
            [f'table_add("{table_name}", "{action_name}", {match_keys_str}, {action_params_str}, {prio})']
        )
        return self._run_cmd(switch_name, command)

    def bmv2_table_get_entry_handle(
        self,
        switch_name: str,
        table_name: str,
        match_keys: List[str],
    ) -> list[str]:
        """
        Get the entry handle of a table given the match keys.
        """
        match_keys_str = _quote_list_double(match_keys)
        command = _build_thrift_command([f'get_handle_from_match("{table_name}", {match_keys_str})'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_set_timeout(
        self,
        switch_name: str,
        table_name: str,
        entry_handle: str,
        timeout_ms: int,
    ) -> list[str]:
        """
        Set the timeout of a table entry. The table has to support timeouts.
        """
        command = _build_thrift_command([f'table_set_timeout("{table_name}", "{entry_handle}", {timeout_ms})'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_modify(
        self,
        switch_name: str,
        table_name: str,
        action_name: str,
        entry_handle: str,
        action_params: List[str] = [],
    ) -> list[str]:
        """
        Modify an entry in a table.
        """
        action_params_str = _quote_list_double(action_params)
        command = _build_thrift_command(
            [f'table_modify("{table_name}", "{action_name}", {entry_handle}, {action_params_str})']
        )
        return self._run_cmd(switch_name, command)

    def bmv2_table_modify_match(
        self,
        switch_name: str,
        table_name: str,
        action_name: str,
        match_keys: List[str],
        action_params: List[str] = [],
    ) -> list[str]:
        """
        Modify entry in a table using match keys.
        """
        match_keys_str = _quote_list_double(match_keys)
        action_params_str = _quote_list_double(action_params)
        command = _build_thrift_command(
            [f'table_modify_match("{table_name}", "{action_name}", {match_keys_str}, {action_params_str})']
        )
        return self._run_cmd(switch_name, command)

    def bmv2_table_delete(
        self,
        switch_name: str,
        table_name: str,
        entry_handle: str,
    ) -> list[str]:
        """
        Delete an entry from a table.
        """
        command = _build_thrift_command([f'table_delete("{table_name}", "{entry_handle}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_delete_match(
        self,
        switch_name: str,
        table_name: str,
        match_keys: List[str],
    ) -> list[str]:
        """
        Delete an entry from a table using match keys.
        """
        match_keys_str = _quote_list_double(match_keys)
        command = _build_thrift_command([f'table_delete_match("{table_name}", {match_keys_str})'])
        return self._run_cmd(switch_name, command)

    # Counter related API
    def bmv2_get_counter_arrays(self, switch_name: str) -> list[str]:
        """
        Show all counter_arrays of a switch.
        """
        command = _build_thrift_command(["get_counter_arrays()"])
        return self._run_cmd(switch_name, command)

    def bmv2_counter_read(
        self,
        switch_name: str,
        counter_name: str,
        index: int = 0,
    ) -> list[str]:
        """
        Read a counter.
        """
        command = _build_thrift_command([f'counter_read("{counter_name}", {index})'])
        return self._run_cmd(switch_name, command)

    def tc_set_intf(
        self,
        host_name: str,
        interface: str,
        loss: int = None,
        delay: int = None,
        jitter: int = None,
        duplicate: int = None,
        corrupt: int = None,
        reorder: int = None,
        rate: int = None,
    ) -> list[str]:
        """
        Set traffic control (tc) parameters on a specific interface of a host.

        Args:
        host_name (str): Name of the host where the interface is located. (could be a switch or normal host)
        interface (str): Interface name (e.g., eth0, eth1).
        loss (int, optional): Packet loss percentage (0-100). Defaults to None.
        delay (int, optional): Delay in milliseconds. Defaults to None.
        jitter (int, optional): Jitter in milliseconds. Defaults to None.
        duplicate (int, optional): Duplicate percentage (0-100). Defaults to None.
        reorder (int, optional): Reorder percentage (0-100). Defaults to None.
        corrupt (int, optional): Corruption percentage (0-100). Defaults to None.
        rate (str, optional): Rate limit in bits per second (e.g., "100"). Defaults to None.
        """
        command = f"tc qdisc add dev {interface} root netem"
        if loss is not None:
            command += f" loss {loss}%"
        if delay is not None:
            command += f" delay {delay}ms"
        if jitter is not None:
            assert delay is not None, "delay must be set before jitter"
            command += f" delay {delay}ms {jitter}ms"
        if duplicate is not None:
            command += f" duplicate {duplicate}%"
        if reorder is not None:
            command += f" reorder {reorder}%"
        if corrupt is not None:
            command += f" corrupt {corrupt}%"
        if rate is not None:
            command += f" rate {rate}mbit"
        return self._run_cmd(host_name, command)

    def tc_show_intf(self, host_name: str, interface: str) -> list[str]:
        """
        Show traffic control (tc) parameters on a specific interface of a host.
        """
        command = f"tc qdisc show dev {interface}"
        return self._run_cmd(host_name, command)

    def tc_clear_intf(self, host_name: str, interface: str) -> list[str]:
        """
        Clear traffic control (tc) parameters on a specific interface of a host.
        """
        command = f"tc qdisc del dev {interface} root"
        return self._run_cmd(host_name, command)


# async def main():
#     lab_name = "simple_bmv2"
#     kathara_api = KatharaAPI(lab_name)
#     result = await kathara_api.get_reachability()
#     print(result)


if __name__ == "__main__":
    lab_name = "simple_bmv2"
    kathara_api = KatharaAPI(lab_name)
    print(kathara_api.get_reachability())
    kathara_api.tc_set_intf(
        host_name="s1",
        interface="eth1",
        loss=90,
        delay=100,
        jitter=10,
        duplicate=0,
        reorder=0,
        corrupt=0,
        rate=100,
    )
    print(kathara_api.tc_show_intf(host_name="s1", interface="eth1"))
    print(kathara_api.get_reachability())
    kathara_api.tc_clear_intf(host_name="s1", interface="eth1")
    print(kathara_api.tc_show_intf(host_name="s1", interface="eth1"))
