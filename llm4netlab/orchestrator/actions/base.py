import re

from llm4netlab.service.kathara import KatharaBMv2API
from llm4netlab.utils.actions import read


class AcionBase:
    """Base class for all actions."""

    @staticmethod
    @read
    def bmv2_get_log(net_env_name: str, switch_name: str) -> str:
        """Get the logs from the bmv2 switch.

        Args:
            net_env_name (str): The name of the lab.
            switch_name (str): The name of the switch.

        Returns:
            str: The logs from the bmv2 switch.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        return kathara_api.bmv2_get_log(switch_name)

    # @staticmethod
    # @read
    # def get_connectivity(net_env_name: str) -> str:
    #     """Get the connectivity of the network.

    #     Args:
    #         net_env_name (str): The name of the lab.

    #     Returns:
    #         str: The connectivity of the lab.
    #     """
    #     kathara_api = KatharaAPI(lab_name=net_env_name)
    #     return kathara_api.get_connectivity()

    @staticmethod
    @read
    def get_reachability(net_env_name: str) -> str:
        """Get the reachability of the lab. From each host, it checks if it can ping all other hosts.

        Args:
            net_env_name (str): The name of the lab.

        Returns:
            str: The ping results from each host to all other hosts in the lab.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        return kathara_api.get_reachability()

    @staticmethod
    @read
    def bmv2_get_counter_names(net_env_name: str, switch_name: str) -> str:
        """Get the counters from the bmv2 switch.

        Args:
            net_env_name (str): The name of the lab.
            switch_name (str): The name of the switch.

        Returns:
            str: The counters from the bmv2 switch.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        counters = kathara_api.bmv2_get_counter_arrays(switch_name)
        matches = re.findall(r"'([^']+)'\s*:", counters)
        return str(matches)

    @staticmethod
    @read
    def bmv2_counter_read(net_env_name: str, switch_name: str, counter_name: str, index: int) -> str:
        """Read a specific counter from the bmv2 switch.

        Args:
            net_env_name (str): The name of the lab.
            switch_name (str): The name of the switch.
            counter_name (str): The name of the counter.
            index (int): The index of the counter to read. Starting from 1. E.g., 1 for port 1, 2 for port 2, etc.

        Returns:
            str: The value of the specified counter.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        return kathara_api.bmv2_counter_read(switch_name, counter_name, index)

    @staticmethod
    @read
    def bmv2_show_ports(net_env_name: str, switch_name: str) -> str:
        """Get the ports of the bmv2 switch.

        Args:
            net_env_name (str): The name of the lab.
            switch_name (str): The name of the switch.

        Returns:
            str: The ports of the bmv2 switch.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        return kathara_api.bmv2_show_ports(switch_name)

    @staticmethod
    @read
    def bmv2_show_tables(net_env_name: str, switch_name: str) -> str:
        """Get the tables of the bmv2 switch.

        Args:
            net_env_name (str): The name of the lab.
            switch_name (str): The name of the switch.

        Returns:
            str: The tables of the bmv2 switch.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        return kathara_api.bmv2_show_tables(switch_name)

    @staticmethod
    @read
    def bmv2_table_dump(net_env_name: str, switch_name: str, table_name: str) -> str:
        """Dump the entries of a specific table in the bmv2 switch.

        Args:
            net_env_name (str): The name of the lab.
            switch_name (str): The name of the switch.
            table_name (str): The name of the table to dump.

        Returns:
            str: The entries of the specified table.
        """
        kathara_api = KatharaBMv2API(lab_name=net_env_name)
        return kathara_api.bmv2_table_dump(switch_name, table_name)


if __name__ == "__main__":
    # Example usage
    action = AcionBase()
    # print(action.bmv2_get_log("simple_bmv2", "s1"))
    # print(action.get_connectivity("simple_bmv2"))
    print(action.get_reachability("simple_bmv2"))
    # print(action.bmv2_get_counter_names("simple_bmv2", "s1"))
    # print(action.bmv2_counter_read("simple_bmv2", "s1", "ingress_port_counter", 1))
    # print(action.bmv2_counter_read("simple_bmv2", "s1", "egress_port_counter", 1))

    # print(action.bmv2_show_ports("simple_bmv2", "s1"))
    # print(action.bmv2_show_tables("simple_bmv2", "s1"))
    # print(action.bmv2_table_dump("simple_bmv2", "s1", "dmac_forward"))
