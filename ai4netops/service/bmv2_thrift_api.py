from typing import Any, Dict, List

from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.thrift_API import BmActionEntryType, MatchType, ResType, hexstr


class Bmv2ThriftAPI:
    """Wrapper class for the SimpleSwitchThriftAPI class.

    Modified the functions that only print instead of returning values.
    """

    def __init__(self, thrift_port: int, thrift_ip: str = "localhost"):
        self.thrift_api = SimpleSwitchThriftAPI(thrift_port, thrift_ip)

    """ Switch Operations. """

    """ Table Operations. """

    def get_table_names(self) -> list:
        """Lists all tables' names defined in the P4 program.

        Note: The origianl input includes the table object, which is not needed for agent to process.
        """
        return list(self.thrift_api.get_tables().keys())

    def get_action_names(self) -> list:
        """Lists actions defined in the P4 program."""
        return list(self.thrift_api.get_actions().keys())

    def get_table_actions(self, table_name: str) -> List[Dict[str, Any]]:
        """Lists one table's actions as per the P4 program.

        Args:
            table_name (str): name of the table
        """
        table = self.thrift_api.get_res("table", table_name, ResType.table)
        actions = []
        for action_name in sorted(table.actions):
            action = table.actions[action_name]
            actions.append(
                {
                    "name": action_name,
                    # "action_str": self.switch_info.actions[action_name].action_str(),
                    "params": action.runtime_data,
                }
            )
        return actions

    def table_num_entries(self, table_name: str) -> int:
        """Returns the number of entries in a match table (direct or indirect).

        Args:
            table_name (str): name of the table

        Returns:
            int: the number of entries in a table.
        """
        return self.thrift_api.table_num_entries(table_name)

    def dump_one_entry(self, table, entry):
        """Dumps one entry from a table.

        Args:
            table (Table): table handle
            entry (Entry): entry handle
        """

        def dump_exact(p):
            return hexstr(p.exact.key)

        def dump_lpm(p):
            return "{}/{}".format(hexstr(p.lpm.key), p.lpm.prefix_length)

        def dump_ternary(p):
            return "{} &&& {}".format(hexstr(p.ternary.key), hexstr(p.ternary.mask))

        def dump_range(p):
            return "{} -> {}".format(hexstr(p.range.start), hexstr(p.range.end_))

        def dump_valid(p):
            return "01" if p.valid.key else "00"

        pdumpers = {
            "exact": dump_exact,
            "lpm": dump_lpm,
            "ternary": dump_ternary,
            "valid": dump_valid,
            "range": dump_range,
        }

        res_entry = {}
        for p, k in zip(entry.match_key, table.key):
            assert k[1] == p.type
            pdumper = pdumpers[MatchType.to_str(p.type)]
            res_entry["name"] = k[0]
            res_entry["match_type"] = MatchType.to_str(p.type).upper()
            res_entry["value"] = pdumper(p)
        if entry.options.priority >= 0:
            res_entry["priority"] = entry.options.priority
        if (
            entry.action_entry.action_type == BmActionEntryType.ACTION_DATA
        ):  # only consider simple entries with action data
            res_entry["action_name"] = entry.action_entry.action_name
            res_entry["action_data"] = ", ".join([hexstr(a) for a in entry.action_entry.action_data])

        if entry.life is not None:
            res_entry["timeout_ms"] = entry.life.timeout_ms
            res_entry["time_since_hit_ms"] = entry.life.time_since_hit_ms

        return res_entry

    def table_dump(self, table_name: str) -> List[Dict[str, Any]]:
        """Lists all entries in a match table.
        #TODO: add support for indirect tables and default entries.

        Args:
            table_name (str): name of the table

        Returns:
            list: list of entries in the table.
        """
        table = self.thrift_api.get_res("table", table_name, ResType.table)
        entry_handles = self.thrift_api.client.bm_mt_get_entries(0, table.name)
        res_entries = []

        for entry in entry_handles:
            res_entries.append(self.dump_one_entry(table, entry))
        return res_entries

    # def table_add(self, table_name: str, action_name: str, action_params: list, match_fields: list, prio=0):
    #     """Adds entry to a match table.

    #     Args:
    #         table_name (str)    : name of the table
    #         action_name (str)   : name of the action to execute
    #         match_keys (list)   : list of matches in the order they appear in the P4 code
    #         action_params (list): list of action parameters in the
    #                               order they appear in the P4 code
    #         prio (int)          : priority in ternary matches

    #     Returns:
    #         int: entry handle.

    #     Note:
    #         - In ``action_params`` and ``match_keys``, action parameters and match keys
    #           must be :py:class:`str`.
    #         - A higher ``prio`` number indicates that the entry must be given higher
    #           priority when performing a table lookup.
    #     """
    #     return self.thrift_api.table_add(table_name, action_name, action_params, match_fields, prio)

    # def table_set_timeout(self, table_name, entry_handle, timeout_ms):
    #     """Sets a timeout in ms for a given entry; the table has to support timeouts.

    #     Args:
    #         table_name (str)  : name of the table
    #         entry_handle (int): entry handle
    #         timeout_ms (int)  : entry timeout in ms
    #     """
    #     return self.thrift_api.table_set_timeout(table_name, entry_handle, timeout_ms)

    # def table_modify(self, table_name, action_name, match_keys, action_params=[]):
    #     """Modifies entry of a match table using match keys.

    #     Args:
    #         table_name (str)        : name of the table
    #         action_name (str)       : name of the action
    #         match_keys (list)       : list of matches in the order they appear in the P4 code
    #         action_params (list): list of action parameters in the
    #                                   order they appear in the P4 code

    #     Returns:
    #         int: entry handle.

    #     Note:
    #         In ``action_params``, action parameters must be :py:class:`str`.
    #     """
    #     return self.thrift_api.table_modify_match(table_name, action_name, match_keys, action_params)

    # def table_delete(self, table_name, match_keys):
    #     """Deletes entry from a table using match keys.

    #     Args:
    #         table_name (str): name of the table
    #         match_keys (list): list of matches in the order they appear in the P4 code

    #     Note:
    #         In ``match_keys``, match keys must be :py:class:`str`.

    #     Warning:
    #         This may not work with ternary matches and priority entries.
    #     """
    #     return self.thrift_api.table_delete_match(table_name, match_keys)

    # def table_clear(self, table_name):
    #     """Clears all entries in a match table (direct or indirect), but not the default entry.

    #     Args:
    #         table_name (str): name of the table
    #     """
    #     return self.controller.table_clear(table_name)

    # """ Counter Operations """

    # """ Port Operations"""


if __name__ == "__main__":
    switch_client = Bmv2ThriftAPI(9090)
    tables = switch_client.get_table_names()
    assert type(tables) == list and len(tables) > 0

    actions = switch_client.get_action_names()
    assert type(actions) == list and len(actions) > 0

    # get the first table
    table_name = tables[0]
    table_actions = switch_client.get_table_actions(table_name)
    assert type(table_actions) == list and len(table_actions) > 0

    num_entries = switch_client.table_num_entries(table_name)
    table_entries = switch_client.table_dump(table_name)
    for entry in table_entries:
        print(entry)
    # table_info = switch_client.table_info(table_name)
    # print(table_info)
    # action_info = switch_client.table_show_actions(table_name)
    # print(action_info)
    # num_entries = switch_client.table_num_entries(table_name)
    # print(num_entries)
