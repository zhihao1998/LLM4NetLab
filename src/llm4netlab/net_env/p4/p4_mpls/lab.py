import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from llm4netlab.config import BASE_DIR
from llm4netlab.net_env.base import NetworkEnvBase

cur_path = os.path.dirname(os.path.abspath(__file__))


class P4_MPLS(NetworkEnvBase):
    LAB_NAME = "p4_mpls"
    TOPO_LEVEL = "medium"
    TOPO_SIZE = None
    TAGS = ["link", "host", "p4", "mac", "arp", "icmp", "mpls"]

    def _add_link(self, device_a: str, device_b: str):
        self.lab.connect_machine_to_link(device_a, f"{device_a}_to_{device_b}")
        self.lab.connect_machine_to_link(device_b, f"{device_a}_to_{device_b}")

    def __init__(self, **kwargs):
        super().__init__()
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "A MPLS network using Bmv2 switches"

        host_1 = self.lab.new_machine("host_1", **{"image": "kathara/base"})
        host_2 = self.lab.new_machine("host_2", **{"image": "kathara/base"})
        host_3 = self.lab.new_machine("host_3", **{"image": "kathara/base"})

        switches = {}
        for i in range(1, 8):
            switch = self.lab.new_machine(
                f"switch_{i}",
                **{"image": "kathara/p4", "cpus": 0.5, "mem": "256m"},
            )
            switches[f"switch_{i}"] = switch

        self._add_link(host_1.name, "switch_1")
        self._add_link("switch_1", "switch_2")
        self._add_link("switch_1", "switch_3")
        self._add_link("switch_2", "switch_4")
        self._add_link("switch_3", "switch_4")
        self._add_link("switch_4", "switch_5")
        self._add_link("switch_4", "switch_6")
        self._add_link("switch_5", "switch_7")
        self._add_link("switch_6", "switch_7")
        self._add_link("switch_7", host_2.name)
        self._add_link("switch_7", host_3.name)

        # Add basic configuration to the machines
        for i in range(1, 4):
            self.lab.create_file_from_path(
                os.path.join(cur_path, f"startups/host_{i}.startup"),
                f"host_{i}.startup",
            )
        for i in range(1, 8):
            self.lab.create_file_from_path(
                os.path.join(cur_path, f"startups/switch_{i}.startup"),
                f"switch_{i}.startup",
            )

        # add cmds
        for i in range(1, 8):
            sw = switches[f"switch_{i}"]
            sw.create_file_from_path(
                os.path.join(cur_path, "mpls.p4"),
                "mpls.p4",
            )
            sw.create_file_from_path(os.path.join(cur_path, f"cmds/switch_{i}/commands.txt"), "commands.txt")

            # add the switch_thrift_API.py file to the Kathara image
            sw.create_file_from_path(
                os.path.join(BASE_DIR, "src/llm4netlab/net_env/utils/p4/sswitch_thrift_API.py"),
                "/usr/local/lib/python3.11/site-packages/sswitch_thrift_API.py",
            )
            sw.create_file_from_path(
                os.path.join(BASE_DIR, "src/llm4netlab/net_env/utils/p4/thrift_API.py"),
                "/usr/local/lib/python3.11/site-packages/thrift_API.py",
            )

        # load machines
        self.load_machines()


if __name__ == "__main__":
    l2 = P4_MPLS()
    print(l2.get_info())

    if l2.lab_exists():
        print("Lab exists, undeploying it...")
        l2.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # l2.deploy()
    # print("Lab deployed")
