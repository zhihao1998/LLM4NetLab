import asyncio
import re
import time
from typing import Dict, Literal, Protocol, runtime_checkable

from Kathara.manager.docker.stats.DockerLinkStats import DockerLinkStats
from Kathara.manager.Kathara import Kathara, Lab
from Kathara.model.Machine import Machine


@runtime_checkable
class _SupportsBase(Protocol):
    instance: "Kathara"
    lab: "Lab"

    def _run_cmd(self, machine_name: str, command: str) -> str: ...


class KatharaBaseAPI:
    """
    Base interfaces to interact with the Kathara.
    """

    def __init__(self, lab_name: str):
        self.instance = Kathara.get_instance()
        self.lab = self.instance.get_lab_from_api(lab_name=lab_name)
        if self.lab is None:
            raise ValueError(f"Lab {lab_name} not found.")

    def get_hosts(self) -> list[Machine]:
        """
        Get the list of hosts (all containers with Docker image kathara/base) in the lab.
        """
        hosts = []
        for name, machine in self.lab.machines.items():
            image = machine.get_image()
            if "base" in image:
                hosts.append(name)
        return hosts

    def get_host_net_config(self, host_name: str) -> dict:
        """
        Get the network configuration of a host, including ifconfig, ip addr, and ip route.
        """
        config = {}
        config["host_name"] = host_name
        config["ifconfig"] = self._run_cmd(host_name, "ifconfig -a")
        config["ip_addr"] = self._run_cmd(host_name, "ip addr")
        config["ip_route"] = self._run_cmd(host_name, "ip route")
        return config

    def get_bmv2_switches(self) -> list[Machine]:
        """
        Get the list of bmv2 switches in the lab.
        """
        switches = []
        for name, machine in self.lab.machines.items():
            image = machine.get_image()
            if "p4" in image:
                switches.append(name)
        return switches

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

    def _run_cmd(self, machine_name: str, command: str) -> str:
        """
        Run a command on a machine and return its output as a string,
        decoding bytes and filtering out None/empty/zeros.
        """
        output_generator = self.instance.exec(
            machine_name=machine_name, command=command, lab_name=self.lab.name, stream=False
        )

        for item in output_generator:
            if not item or item == b"" or isinstance(item, int) or item is None or item == "None":
                continue
            if isinstance(item, bytes):
                return item.decode("utf-8", errors="ignore").strip()
            elif isinstance(item, str):
                return item.strip()
            else:
                return str(item).strip()

        return ""

    def exec_cmd(self, machine_name: str, command: str) -> str:
        """
        Run a command on a machine and return its output as a string.
        """
        cmd = "/bin/bash -c '{}'".format(command.replace("'", "'\\''").replace('"', '\\"'))
        return self._run_cmd(machine_name, cmd)

    # asynchronous
    async def _run_cmd_async(self, machine_name: str, command: str) -> list[str]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._run_cmd, machine_name, command)

    async def _check_ping_success_async(self, host: str, dst_ip: str) -> bool:
        command = f"ping -c 4 {dst_ip}"
        result = await self._run_cmd_async(host, command)
        # matches = re.findall(r"\d+ packets transmitted, \d+ received, .*? packet loss, time \d+ms", result)
        # if len(matches) > 0:
        #     return matches[0]
        # else:
        return result

    async def get_reachability(self) -> str:
        return await self._get_reachability_async()

    async def _get_reachability_async(self) -> str:
        host_names = [host for host in self.get_hosts()]
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

    def ping_pair(self, host_a: str, host_b: str, count: int = 4) -> str:
        """
        Ping from one host to another in the lab.
        """
        command = f"ping -c {count} {self.get_host_ip(host_b)}"
        return self._run_cmd(host_a, command)

    def traceroute(self, host_name: str, dst_ip: str) -> str:
        """
        Run a traceroute from a host to a destination IP.
        """
        command = f"traceroute {dst_ip}"
        return self._run_cmd(host_name, command)

    def iperf_test(
        self,
        client_host_name: str,
        server_host_name: str,
        duration: int = 10,
        client_args: str = "",
        server_args: str = "",
    ) -> str:
        """
        Run an iperf test between two hosts.
        """
        # Start iperf server
        self._run_cmd(server_host_name, f"iperf3 -s -D {server_args}")
        # Run iperf client
        result = self._run_cmd(
            client_host_name, f"iperf3 -c {self.get_host_ip(server_host_name)} -t {duration} {client_args}"
        )
        # Stop iperf server
        self._run_cmd(server_host_name, "pkill iperf3")
        return result

    def systemctl_ops(
        self, host_name: str, service_name: str, operation: Literal["start", "stop", "restart", "status"]
    ) -> str:
        """
        Perform systemctl operations (start, stop, restart, status) on a host.
        """
        result = self._run_cmd(host_name, f"systemctl {operation} {service_name}")
        if operation != "status":
            time.sleep(5)
        return result

    def netstat(self, host_name: str, args: str = "-tuln") -> str:
        """
        Run netstat command on a host with given arguments.
        Example: -s for statistics, -tuln for listening ports.
        """
        command = f"netstat {args}"
        return self._run_cmd(host_name, command)

    def ip_addr_statistics(self, host_name: str) -> str:
        """
        Get IP address statistics of a host.
        """
        command = "ip -s addr"
        return self._run_cmd(host_name, command)

    def ethtool(self, host_name: str, interface: str, args: str = "") -> str:
        """
        Run ethtool command on a specific interface of a host with given arguments.
        """
        command = f"ethtool {interface} {args}"
        return self._run_cmd(host_name, command)

    def curl_web_test(self, host_name: str, url: str, times: int = 5) -> str:
        """
        Perform a curl web test to a URL for several times and return timing statistics.
        """
        command = (
            f"curl -w 'namelookup:%{{time_namelookup}}, "
            f"connect:%{{time_connect}}, "
            f"appconnect:%{{time_appconnect}}, "
            f"pretransfer:%{{time_pretransfer}}, "
            f"starttransfer:%{{time_starttransfer}}, "
            f"total:%{{time_total}}\\n' "
            f"-o /dev/null -s {url}"
        )
        res = ""
        for _ in range(times):
            res += self._run_cmd(host_name, command) + "\n"
        return res.strip()

    def ps(self, host_name: str, args: str = "aux") -> str:
        """
        Run ps command on a host with given arguments.
        Example: aux for all processes.
        """
        command = f"ps {args}"
        return self._run_cmd(host_name, command)

    def show_dns_config(self, host_name: str) -> str:
        """
        Show DNS configuration of a host.
        """
        command = "cat /etc/resolv.conf"
        return self._run_cmd(host_name, command)


async def main():
    api = KatharaBaseAPI(lab_name="dc_clos_service")
    result = api.curl_web_test("client_0", "http://web0.pod0")
    # result = await api.ping_pair("client_0", "webserver0_pod0", count=4)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
