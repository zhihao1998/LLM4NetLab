import asyncio
import json
import re
from typing import Dict, Protocol, runtime_checkable

from Kathara.manager.docker.stats.DockerLinkStats import DockerLinkStats
from Kathara.manager.Kathara import Kathara, Lab
from Kathara.model.Machine import Machine


@runtime_checkable
class _SupportsBase(Protocol):
    instance: "Kathara"
    lab: "Lab"

    def _run_cmd(self, machine_name: str, command: str) -> list[str]: ...


class KatharaBaseAPI:
    """
    Base interfaces to interact with the Kathara.
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

    def _run_cmd(self, machine_name: str, command: str) -> str:
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


if __name__ == "__main__":
    lab_name = "simple_bmv2"
    kathara_api = KatharaBaseAPI(lab_name)
    print(kathara_api.get_reachability())
