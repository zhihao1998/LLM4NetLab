import asyncio
from typing import List

from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


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


class BMv2APIMixin:
    """
    Interfaces to interact with the Kathara BMv2 switches.
    """

    # Log related API
    def bmv2_get_log(self: _SupportsBase, switch_name: str, rows: int = 100) -> list[str]:
        """
        Get the log file of a switch.
        """
        command = f"tail -n {rows} sw.log"
        return self._run_cmd(switch_name, command)

    # Switch related API
    def bmv2_switch_info(self: _SupportsBase, switch_name: str) -> list[str]:
        """
        Show the switch info.
        """
        command = _build_thrift_command(["show_switch_info()"])
        return self._run_cmd(switch_name, command)

    def bmv2_show_ports(self: _SupportsBase, switch_name: str) -> list[str]:
        """
        Show the ports of a switch.
        """
        command = _build_thrift_command(["show_ports()"])
        return self._run_cmd(switch_name, command)

    def bmv2_show_tables(self: _SupportsBase, switch_name: str) -> list[str]:
        """
        Show the tables of a switch.
        """
        command = _build_thrift_command(["show_tables()"])
        return self._run_cmd(switch_name, command)

    def bmv2_show_actions(self: _SupportsBase, switch_name: str) -> list[str]:
        """
        Show all actions of a switch.
        """
        command = _build_thrift_command(["show_actions()"])
        return self._run_cmd(switch_name, command)

    def bmv2_get_register_arrays(self: _SupportsBase, switch_name: str) -> list[str]:
        """
        Show all register_arrays of a switch.
        """
        command = _build_thrift_command(["get_register_arrays()"])
        return self._run_cmd(switch_name, command)

    # Table related API
    def bmv2_table_info(self: _SupportsBase, switch_name: str, table_name: str) -> list[str]:
        """
        Show the info of a table.
        """
        command = _build_thrift_command([f'table_info("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_dump(self: _SupportsBase, switch_name: str, table_name: str) -> list[str]:
        """
        Dump the content of a table.
        """
        command = _build_thrift_command([f'table_dump("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_show_actions(self: _SupportsBase, switch_name: str, table_name: str) -> list[str]:
        """
        Show the actions of a table.
        """
        command = _build_thrift_command([f'table_show_actions("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_num_entries(self: _SupportsBase, switch_name: str, table_name: str) -> list[str]:
        """
        Show the number of entries in a table.
        """
        command = _build_thrift_command([f'table_num_entries("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_clear(self: _SupportsBase, switch_name: str, table_name: str) -> list[str]:
        """
        Clear the content of a table.
        """
        command = _build_thrift_command([f'table_clear("{table_name}")'])
        return self._run_cmd(switch_name, command)

    def bmv2_table_add(
        self: _SupportsBase,
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
        self: _SupportsBase,
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
        self: _SupportsBase,
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
        self: _SupportsBase,
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
        self: _SupportsBase,
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
        self: _SupportsBase,
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
        self: _SupportsBase,
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
    def bmv2_get_counter_arrays(self: _SupportsBase, switch_name: str) -> list[str]:
        """
        Show all counter_arrays of a switch.
        """
        command = _build_thrift_command(["get_counter_arrays()"])
        return self._run_cmd(switch_name, command)

    def bmv2_counter_read(
        self: _SupportsBase,
        switch_name: str,
        counter_name: str,
        index: int = 0,
    ) -> list[str]:
        """
        Read a counter.
        """
        command = _build_thrift_command([f'counter_read("{counter_name}", {index})'])
        return self._run_cmd(switch_name, command)

    def read_p4_program(
        self: _SupportsBase,
        switch_name: str,
    ) -> list[str]:
        """
        Read the P4 program from the switch.
        """
        command = "cat *.p4"
        return self._run_cmd(switch_name, command)


class KatharaBMv2API(KatharaBaseAPI, BMv2APIMixin):
    """
    Kathara API for interacting with BMv2 switches.
    """

    pass


async def main():
    lab_name = "p4_mpls"
    kathara_api = KatharaBMv2API(lab_name)
    # result = await kathara_api.get_reachability()
    # print(result)

    result = kathara_api.bmv2_table_dump("switch_1", "MyIngress.mpls_tbl")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
