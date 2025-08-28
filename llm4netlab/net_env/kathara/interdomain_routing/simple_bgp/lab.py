import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from llm4netlab.net_env.base import NetworkEnvBase

LAB_NAME = "simple_bgp"
cur_path = os.path.dirname(os.path.abspath(__file__))


class SimpleBGP(NetworkEnvBase):
    def __init__(self):
        self.lab = Lab(LAB_NAME)
        self.name = LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "A simple BGP network with two routers and two hosts."

        router1 = self.lab.new_machine("router1", **{"image": "kathara/frr"})
        router2 = self.lab.new_machine("router2", **{"image": "kathara/frr"})

        pc1 = self.lab.new_machine("pc1", **{"image": "kathara/base"})
        pc2 = self.lab.new_machine("pc2", **{"image": "kathara/base"})

        self.lab.connect_machine_to_link(router1.name, "A")
        self.lab.connect_machine_to_link(router2.name, "A")

        self.lab.connect_machine_to_link(router1.name, "B")
        self.lab.connect_machine_to_link(pc1.name, "B")

        self.lab.connect_machine_to_link(router2.name, "C")
        self.lab.connect_machine_to_link(pc2.name, "C")

        # Add basic configuration to the machines
        for i, router in enumerate([router1, router2], start=1):
            router.copy_directory_from_path(os.path.join(cur_path, f"router{i}/etc"), "/etc")
            # to create the startup file, use self.lab instead of host
            self.lab.create_file_from_path(os.path.join(cur_path, f"router{i}.startup"), f"router{i}.startup")

        for i, host in enumerate([pc1, pc2], start=1):
            self.lab.create_file_from_path(os.path.join(cur_path, f"pc{i}.startup"), f"pc{i}.startup")


if __name__ == "__main__":
    simple_bgp = SimpleBGP()
    print(simple_bgp)
    if simple_bgp.lab_exists():
        print("Lab exists, undeploying it...")
        simple_bgp.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # simple_bgp.deploy()
    # print("Lab deployed")
