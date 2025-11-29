from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


class TCMixin:
    """
    Interfaces to interact with Linux Traffic within Kathara.
    """

    def tc_set_netem(
        self: _SupportsBase,
        host_name: str,
        intf_name: str,
        loss: int = None,
        delay_ms: int = None,
        jitter_ms: int = None,
        duplicate: int = None,
        corrupt: int = None,
        reorder: int = None,
        limit: int = None,
        handle: str = None,
        parent: str = None,
    ) -> list[str]:
        """
        Set traffic control (tc) netem qdisc on a specific intf_name of a host.

        Args:
        host_name (str): Name of the host where the intf_name is located. (could be a switch or normal host)
        intf_name (str): Interface name (e.g., eth0, eth1).
        loss (int, optional): Packet loss percentage (0-100). Defaults to None.
        delay_ms (int, optional): Delay in milliseconds. Defaults to None.
        jitter_ms (int, optional): Jitter in milliseconds. Defaults to None.
        duplicate (int, optional): Duplicate percentage (0-100). Defaults to None.
        reorder (int, optional): Reorder percentage (0-100). Defaults to None.
        corrupt (int, optional): Corruption percentage (0-100). Defaults to None.
        limit (int, optional): Queue size limit. Defaults to None.
        handle (str, optional): qdisc handle, e.g. "1:" or "1". Defaults to None.
        parent (str, optional): parent class/qdisc, e.g. "1:1". Defaults to None.
        """

        command = f"tc qdisc add dev {intf_name}"

        if parent is not None:
            command += f" parent {parent}"
        else:
            command += " root"

        if handle is not None:
            if not handle.endswith(":"):
                handle = handle + ":"
            command += f" handle {handle}"

        command += " netem"

        if loss is not None:
            command += f" loss {loss}%"

        if delay_ms is not None and jitter_ms is None:
            command += f" delay {delay_ms}ms"
        elif delay_ms is not None and jitter_ms is not None:
            command += f" delay {delay_ms}ms {jitter_ms}ms"

        if duplicate is not None:
            command += f" duplicate {duplicate}%"
        if reorder is not None:
            command += f" reorder {reorder}%"
        if corrupt is not None:
            command += f" corrupt {corrupt}%"
        if limit is not None:
            command += f" limit {limit}"

        return self._run_cmd(host_name, command)

    def tc_set_tbf(
        self: _SupportsBase,
        host_name: str,
        intf_name: str,
        rate: str,
        burst: str,
        limit: str,
        handle: str = None,
        parent: str = None,
    ) -> list[str]:
        """
        Set Token Bucket Filter (tbf) qdisc on a specific intf_name of a host.

        Args:
        host_name (str): Name of the host where the intf_name is located. (could be a switch or normal host)
        intf_name (str): Interface name (e.g., eth0, eth1).
        rate (str): Rate limit (e.g., "100mbit").
        burst (str): Burst size (e.g., "32kbit").
        limit (str): Limit size (e.g., "10000").
        handle (str, optional): qdisc handle, e.g. "10:" or "10". Defaults to None.
        parent (str, optional): parent class/qdisc, e.g. "1:1". Defaults to None.
        """

        command = f"tc qdisc add dev {intf_name}"

        if parent is not None:
            command += f" parent {parent}"
        else:
            command += " root"

        if handle is not None:
            if not handle.endswith(":"):
                handle = handle + ":"
            command += f" handle {handle}"

        command += f" tbf rate {rate} burst {burst} limit {limit}"

        return self._run_cmd(host_name, command)

    def tc_show_intf(self: _SupportsBase, host_name: str, intf_name: str) -> list[str]:
        """
        Show traffic control (tc) parameters on a specific intf_name of a host.
        """
        command = f"tc qdisc show dev {intf_name}"
        return self._run_cmd(host_name, command)

    def tc_show_statistics(self: _SupportsBase, host_name: str, intf_name: str) -> list[str]:
        """
        Show traffic control (tc) statistics on a specific intf_name of a host.
        """
        command = f"tc -s qdisc show dev {intf_name}"
        return self._run_cmd(host_name, command)

    def tc_clear_intf(self: _SupportsBase, host_name: str, intf_name: str) -> list[str]:
        """
        Clear traffic control (tc) parameters on a specific intf_name of a host.
        """
        command = f"tc qdisc del dev {intf_name} root"
        return self._run_cmd(host_name, command)


class KatharaTCAPI(KatharaBaseAPI, TCMixin):
    """
    Kathara Traffic Control API to manage traffic control settings on host intf_names.
    """

    pass


if __name__ == "__main__":
    lab_name = "p4_counter"
    kathara_api = KatharaTCAPI(lab_name)
    print(kathara_api.get_reachability())
    kathara_api.tc_set_netem(
        host_name="s1",
        intf_name="eth1",
        loss=90,
        delay_ms=100,
        jitter=10,
        duplicate=0,
        reorder=0,
        corrupt=0,
        rate=100,
    )
    print(kathara_api.tc_show_intf(host_name="s1", intf_name="eth1"))
    print(kathara_api.get_reachability())
    kathara_api.tc_clear_intf(host_name="s1", intf_name="eth1")
    print(kathara_api.tc_show_intf(host_name="s1", intf_name="eth1"))
