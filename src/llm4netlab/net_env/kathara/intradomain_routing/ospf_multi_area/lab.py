import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from llm4netlab.net_env.base import NetworkEnvBase

cur_path = os.path.dirname(os.path.abspath(__file__))

"""
pc1       pc2
 |A        |B
  (Area 0)
R1 --E--- R2
 |F        |G
 |         |
R3         R4
(Area 1)   (Area 2)
 |C        |D
pc3       pc4
"""


class OspfMultiArea(NetworkEnvBase):
    LAB_NAME = "ospf_multi_area"

    def __init__(self):
        super().__init__()
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "An OSPF network with 4 routers and 3 areas."

        router1 = self.lab.new_machine("router1", **{"image": "kathara/frr"})
        router2 = self.lab.new_machine("router2", **{"image": "kathara/frr"})
        router3 = self.lab.new_machine("router3", **{"image": "kathara/frr"})
        router4 = self.lab.new_machine("router4", **{"image": "kathara/frr"})

        pc1 = self.lab.new_machine("pc1", **{"image": "kathara/base"})
        pc2 = self.lab.new_machine("pc2", **{"image": "kathara/base"})
        pc3 = self.lab.new_machine("pc3", **{"image": "kathara/base"})
        pc4 = self.lab.new_machine("pc4", **{"image": "kathara/base"})

        self.lab.connect_machine_to_link(router1.name, "A")
        self.lab.connect_machine_to_link(pc1.name, "A")

        self.lab.connect_machine_to_link(router2.name, "B")
        self.lab.connect_machine_to_link(pc2.name, "B")

        self.lab.connect_machine_to_link(router3.name, "C")
        self.lab.connect_machine_to_link(pc3.name, "C")

        self.lab.connect_machine_to_link(router4.name, "D")
        self.lab.connect_machine_to_link(pc4.name, "D")

        self.lab.connect_machine_to_link(router1.name, "E")
        self.lab.connect_machine_to_link(router2.name, "E")

        self.lab.connect_machine_to_link(router1.name, "F")
        self.lab.connect_machine_to_link(router3.name, "F")

        self.lab.connect_machine_to_link(router2.name, "G")
        self.lab.connect_machine_to_link(router4.name, "G")

        # Add basic configuration to the machines
        for i, router in enumerate([router1, router2, router3, router4], start=1):
            router.copy_directory_from_path(os.path.join(cur_path, f"router{i}/etc"), "/etc")
            self.lab.create_file_from_path(os.path.join(cur_path, f"router{i}.startup"), f"router{i}.startup")

        for i, pc in enumerate([pc1, pc2, pc3, pc4], start=1):
            self.lab.create_file_from_path(os.path.join(cur_path, f"pc{i}.startup"), f"pc{i}.startup")


if __name__ == "__main__":
    ospf_multi_area = OspfMultiArea()
    print("Lab description:", ospf_multi_area.desc)
    print("lab net summary:", ospf_multi_area.net_summary())
    if ospf_multi_area.lab_exists():
        print("Lab exists, undeploying it...")
        ospf_multi_area.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # ospf_multi_area.deploy()
    # print("Lab deployed")
