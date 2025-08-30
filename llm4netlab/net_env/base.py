from collections import defaultdict

from Kathara.manager.Kathara import Kathara


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
        self.hosts = None
        self.routers = None
        self.links = None

    def load_machines(self):
        self.bmv2_switches = []
        self.ovs_switches = []
        self.hosts = []
        self.routers = []
        self.links = []
        machines = self.lab.machines
        for machine, machine_obj in machines.items():
            image = machine_obj.get_image()
            if "p4" in image:
                self.bmv2_switches.append(machine)
            elif "frr" in image:
                self.routers.append(machine)
            elif "base" in image:
                self.hosts.append(machine)
            elif "influxdb" in image:
                self.hosts.append(machine)
            elif "sdn" in image:
                self.ovs_switches.append(machine)
            else:
                print(f"Unknown machine type: {machine} with image {image}")

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

    def net_summary(self):
        """
        Generate a summary of the network configuration.
        """
        self.load_machines()
        summary = f"Lab name: {self.name}\nDescription: {self.desc}\n"
        if self.bmv2_switches:
            summary += f"BMV2 switches: {', '.join(self.bmv2_switches)}\n"
        if self.ovs_switches:
            summary += f"OVS switches: {', '.join(self.ovs_switches)}\n"
        if self.hosts:
            summary += f"Hosts: {', '.join(self.hosts)}\n"
        if self.routers:
            summary += f"Routers: {', '.join(self.routers)}\n"
        if self.links:
            summary += f"Links: {', '.join(self.links)}\n"
        summary += f"Topology: {', '.join(f'({a}, {b})' for a, b in self.get_topology())}"
        return summary

    def __str__(self):
        """
        Return a string representation of the network environment.
        """
        return self.net_summary()

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

    def undeploy(self):
        """Undeploy the lab"""
        try:
            self.instance.undeploy_lab(lab_name=self.name)
        except Exception as e:
            print(f"Error undeploying lab {self.name}: {e}")


if __name__ == "__main__":
    net_env = NetworkEnvBase()
    print(net_env)
