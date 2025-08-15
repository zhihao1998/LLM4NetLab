from llm4netlab.service.kathara.base import KatharaBaseAPI, _SupportsBase


class KatharaTCMixin:
    """
    Interfaces to interact with Linux Traffic within Kathara.
    """

    def tc_set_intf(
        self: _SupportsBase,
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

    def tc_show_intf(self: _SupportsBase, host_name: str, interface: str) -> list[str]:
        """
        Show traffic control (tc) parameters on a specific interface of a host.
        """
        command = f"tc qdisc show dev {interface}"
        return self._run_cmd(host_name, command)

    def tc_clear_intf(self: _SupportsBase, host_name: str, interface: str) -> list[str]:
        """
        Clear traffic control (tc) parameters on a specific interface of a host.
        """
        command = f"tc qdisc del dev {interface} root"
        return self._run_cmd(host_name, command)


class KatharaTCAPI(KatharaBaseAPI, KatharaTCMixin):
    """
    Kathara Traffic Control API to manage traffic control settings on host interfaces.
    """

    pass


# async def main():
#     lab_name = "simple_bmv2"
#     kathara_api = KatharaAPI(lab_name)
#     result = await kathara_api.get_reachability()
#     print(result)


if __name__ == "__main__":
    lab_name = "simple_bmv2"
    kathara_api = KatharaTCAPI(lab_name)
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
