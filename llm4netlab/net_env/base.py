import json


class NetworkEnvBase:
    """
    Base class for network environments."""

    def __init__(self, config_file=None):
        self.config_file = config_file
        self.name = None
        self.desc = None
        self.bmv2_switches = []
        self.ovs_switches = []
        self.hosts = []
        self.routers = []
        self.links = []
        self.interfaces = []
        self.load_config()

    def load_config(self):
        """
        Load the network configuration from a file or string.
        """
        assert self.config_file
        with open(self.config_file, "r") as file:
            config = json.load(file)
        self.name = config.get("name")
        self.desc = config.get("description")
        self.nodes = config.get("nodes", None)
        for node in self.nodes:
            if node == "bmv2_switches":
                self.bmv2_switches = config["nodes"][node]
            elif node == "ovs_switches":
                self.ovs_switches = config["nodes"][node]
            elif node == "hosts":
                self.hosts = config["nodes"][node]
            elif node == "routers":
                self.routers = config["nodes"][node]
        self.links = config.get("links", None)

        for bmv2_switch in self.bmv2_switches:
            for intf in config["interfaces"][bmv2_switch]:
                self.interfaces.append(f"{bmv2_switch}:{intf}")

    def net_summary(self):
        """
        Generate a summary of the network configuration.
        """
        summary = f"Network environment name: {self.name}\nDescription: {self.desc}\n"
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
        if self.interfaces:
            summary += f"Interfaces: {', '.join(self.interfaces)}\n"
        return summary

    def __str__(self):
        """
        Return a string representation of the network environment.
        """
        return self.net_summary()

    def deploy(self):
        """
        Deploy the network environment.
        """
        # Implement the deployment logic here
        raise NotImplementedError("Deploy method not implemented.")

    def undeploy(self):
        """
        Undeploy the network environment.
        """
        # Implement the undeployment logic here
        raise NotImplementedError("Undeploy method not implemented.")


if __name__ == "__main__":
    net_env = NetworkEnvBase(
        config_file="/home/p4/codes/llm4netlab/llm4netlab/net_env/kathara/l2_basic_forwarding/metadata.json"
    )
    net_env.load_config()
    print(net_env)
