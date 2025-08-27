from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


class KtharaNFTableMixin:
    """
    Interfaces to interact with nftables within Kathara.
    """

    def nft_list_ruleset(
        self: _SupportsBase,
        host_name: str,
    ) -> list[str]:
        """
        List nftables rules in a specific table and chain on a host.

        Args:
            host_name (str): Name of the host where the nftables rules are to be listed.

        Returns:
            list[str]: The output of the nft list ruleset command.
        """
        command = "nft -a list ruleset"
        return self._run_cmd(host_name, command)

    def nft_list_tables(
        self: _SupportsBase,
        host_name: str,
    ) -> list[str]:
        """
        List nftables tables on a host.

        Args:
            host_name (str): Name of the host where the nftables tables are to be listed.

        Returns:
            list[str]: The output of the nft list tables command.
        """
        command = "nft list tables"
        return self._run_cmd(host_name, command)

    def nft_list_chains(
        self: _SupportsBase,
        host_name: str,
    ) -> list[str]:
        """
        List nftables chains in a specific table on a host.

        Args:
            host_name (str): Name of the host where the nftables chains are to be listed.
            table (str): The nftables table name.

        Returns:
            list[str]: The output of the nft list chains command.
        """
        command = "nft list chains"
        return self._run_cmd(host_name, command)

    def nft_add_table(
        self: _SupportsBase,
        host_name: str,
        table_name: str,
        family: str = "inet",
    ) -> list[str]:
        """
        Add a table to nftables on a host.

        Args:
            host_name (str): Name of the host where the nftables table is to be added.
            table (str): The nftables table name.
            family (str, optional): The nftables family. Defaults to "inet".

        Returns:
            list[str]: The output of the nft add table command.
        """
        command = f"nft add table {family} {table_name}"
        return self._run_cmd(host_name, command)

    def nft_add_chain(
        self: _SupportsBase,
        host_name: str,
        table: str,
        chain: str,
        family: str = "inet",
        hook: str = None,
        type: str = None,
        policy: str = None,
    ) -> list[str]:
        """
        Add a chain to a specific table on a host. Must ensure the table exists.

        Args:
            host_name (str): Name of the host where the nftables chain is to be added.
            table (str): The nftables table name.
            chain (str): The nftables chain name.
            hook (str, optional): The hook name (e.g., "input", "output", "forward"). Defaults to None.
            type (str, optional): The chain type (e.g., "filter", "nat"). Defaults to None.
            policy (str, optional): The default policy for the chain (e.g., "accept", "drop"). Defaults to None.

        Returns:
            list[str]: The output of the nft add chain command.
        """
        command = f"nft add chain {family} {table} {chain}"
        if type and hook:
            command += f" '{{ type {type} hook {hook} priority 0 ;"
            if policy:
                command += f" policy {policy} ;"
            command += " }'"
        return self._run_cmd(host_name, command)

    def nft_add_rule(
        self: _SupportsBase,
        host_name: str,
        table: str,
        chain: str,
        rule: str,
        family: str = "inet",
    ) -> list[str]:
        """
        Add a rule to a specific table and chain on a host. Must ensure the table and chain exist.

        Args:
            host_name (str): Name of the host where the nftables rules are to be listed.
            table (str): The nftables table name.
            chain (str): The nftables chain name.
            rule (str): The rule to be added.
            family (str, optional): The nftables family. Defaults to "inet".

        Returns:
            list[str]: The output of the nft add rule command.
        """
        command = f"nft add rule {family} {table} {chain} {rule}"
        return self._run_cmd(host_name, command)

    def nft_delete_table(
        self: _SupportsBase,
        host_name: str,
        table_name: str,
        family: str = "inet",
    ) -> list[str]:
        """
        Delete a table from nftables on a host.

        Args:
            host_name (str): Name of the host where the nftables table is to be deleted.
            table (str): The nftables table name.
            family (str, optional): The nftables family. Defaults to "inet".

        Returns:
            list[str]: The output of the nft delete table command.
        """
        command = f"nft delete table {family} {table_name}"
        return self._run_cmd(host_name, command)


class KatharaNFTableAPI(KatharaBaseAPI, KtharaNFTableMixin):
    """
    Kathara Traffic Control API to manage nftables within Kathara.
    """

    pass


# async def main():
#     lab_name = "simple_bmv2"
#     kathara_api = KatharaAPI(lab_name)
#     result = await kathara_api.get_reachability()
#     print(result)


if __name__ == "__main__":
    lab_name = "simple_bgp"
    kathara_api = KatharaNFTableAPI(lab_name)
    table_name = "filter"
    family = "inet"

    kathara_api.nft_delete_table(host_name="router1", table=table_name)
    print(kathara_api.nft_list_tables(host_name="router1"))

    kathara_api.nft_add_table(host_name="router1", family=family, table=table_name)
    print(kathara_api.nft_list_tables(host_name="router1"))

    for chain_name in ["INPUT", "FORWARD"]:
        kathara_api.nft_add_chain(
            host_name="router1",
            family=family,
            table=table_name,
            chain=chain_name,
            hook="output",
            type="filter",
            policy="accept",
        )
        kathara_api.nft_add_rule(
            host_name="router1",
            family=family,
            table=table_name,
            chain=chain_name,
            rule="tcp dport 179 drop",
        )
        kathara_api.nft_add_rule(
            host_name="router1",
            family=family,
            table=table_name,
            chain=chain_name,
            rule="tcp sport 179 drop",
        )

    print(kathara_api.nft_list_ruleset(host_name="router1"))
