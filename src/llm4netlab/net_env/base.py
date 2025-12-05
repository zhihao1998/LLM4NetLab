import time
from collections import defaultdict
from typing import Dict

from Kathara.manager.Kathara import Kathara, Machine


class NetworkEnvBase:
    LAB_NAME = None
    """
    Base class for network environments."""

    def __init__(self):
        self.name = None
        self.desc = None
        self.instance = None
        self.lab = None
        self.bmv2_switches = None
        self.ovs_switches = None
        self.sdn_controllers = None
        self.hosts = None
        self.routers = None
        self.links = None
        self.switches = None
        self.servers = None

    def load_machines(self):
        self.bmv2_switches = []
        self.ovs_switches = []
        self.sdn_controllers = []
        self.hosts = []
        self.routers = []
        self.switches = []
        self.servers = defaultdict(list)

        machines: Dict[str, Machine] = self.lab.machines
        for machine, machine_obj in machines.items():
            image = machine_obj.get_image()
            if "p4" in image:
                self.bmv2_switches.append(machine)
            elif "frr" in image:
                self.routers.append(machine)
            elif "base" in image or "nginx" in image or "wireguard" in image:
                host_keys = ["pc", "host", "client"]
                if any(key in machine for key in host_keys):
                    self.hosts.append(machine)
                elif "load_balancer" in machine or "lb" in machine:
                    self.servers["load_balancer"].append(machine)
                elif "switch" in machine or "sw" in machine:
                    self.switches.append(machine)
                elif "dns" in machine:
                    self.servers["dns"].append(machine)
                elif "dhcp" in machine:
                    self.servers["dhcp"].append(machine)
                elif "web" in machine and "backend" not in machine:
                    self.servers["web"].append(machine)
                elif "vpn" in machine:
                    self.servers["vpn"].append(machine)

            elif "influxdb" in image:
                self.servers["database"].append(machine)

            elif "sdn" in image:
                self.ovs_switches.append(machine)
            elif "pox" in image or "ryu" in image:
                self.sdn_controllers.append(machine)
            else:
                print(f"Unknown machine type: {machine} with image {image}")

        # sort all lists
        self.bmv2_switches = sorted(self.bmv2_switches)
        self.ovs_switches = sorted(self.ovs_switches)
        self.sdn_controllers = sorted(self.sdn_controllers)
        self.hosts = sorted(self.hosts)
        self.routers = sorted(self.routers)
        self.switches = sorted(self.switches)
        for server_type in self.servers:
            self.servers[server_type] = sorted(self.servers[server_type])

    def get_topology(self) -> dict:
        """
        Get the topology of the network.

        Output format: [(host1:intf1, host2:intf2), ...]
        """
        topology = defaultdict(list)
        machines = self.lab.machines
        for machine, stat in machines.items():
            for intf_num, intf in stat.interfaces.items():
                topology[intf.link.name].append(f"{machine}:eth{intf_num}")
        # sorted by the link name A, B, C, ...
        topology = sorted(topology.items(), key=lambda x: x[0])
        topo_list = []
        for link, machines in topology:
            topo_list.append((machines[0], machines[1]))
        return topo_list

    def get_info(self):
        """
        Generate a summary of the network configuration.
        """
        self.load_machines()
        summary = f"Network Description: {self.desc}\n"
        if self.bmv2_switches:
            summary += f"BMV2 switches: {', '.join(self.bmv2_switches)}\n"
        if self.ovs_switches:
            summary += f"OVS switches: {', '.join(self.ovs_switches)}\n"
        if self.switches:
            summary += f"Switches: {', '.join(self.switches)}\n"
        if self.hosts:
            summary += f"Hosts: {', '.join(self.hosts)}\n"
        if self.servers:
            for server_type, server_list in self.servers.items():
                summary += f"{server_type.capitalize()} Servers: {', '.join(server_list)}\n"
        if self.routers:
            summary += f"Routers (FRRRouting): {', '.join(self.routers)}\n"
        if self.links:
            summary += f"Links: {', '.join(self.links)}\n"
        summary += f"Topology: {', '.join(f'({a}, {b})' for a, b in self.get_topology())}"
        return summary

    def __str__(self):
        """
        Return a string representation of the network environment.
        """
        return self.get_info()

    def lab_exists(self):
        """Check if the lab exists"""
        tmp_lab = self.instance.get_lab_from_api(lab_name=self.name)
        tmp_machines = tmp_lab.machines
        if len(tmp_machines) == 0 or tmp_machines is None:
            return False
        return True

    def deploy(self):
        """Deploy the lab"""
        if self.lab_exists():
            print(f"Lab {self.name} exists")
            return
        Kathara.get_instance().deploy_lab(lab=self.lab)
        # sleep for a while to let the lab stabilize
        time.sleep(5)

    def undeploy(self):
        """Undeploy the lab"""
        try:
            self.instance.undeploy_lab(lab_name=self.name)
        except Exception as e:
            print(f"Error undeploying lab {self.name}: {e}")


if __name__ == "__main__":
    net_env = NetworkEnvBase()
    print(net_env)
