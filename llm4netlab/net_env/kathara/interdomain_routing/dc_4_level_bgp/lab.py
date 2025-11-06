import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from llm4netlab.net_env.base import NetworkEnvBase

cur_path = os.path.dirname(os.path.abspath(__file__))

r"""
    PC1
    |
    A1             A2
     \             /
      \           /
       \_________/
      /           \
B1 ------- B2 ------- B3
 \          |          /
    \       |       /
        \   |   /
           C1
            |
           D1
           |
           PC2
"""


class IBGPDC4Level(NetworkEnvBase):
    LAB_NAME = "ibgp_dc_4_level"

    def __init__(self):
        super().__init__()
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "An data center network with 4 levels using iBGP routing protocol."

        router_a1 = self.lab.new_machine("router_a1", **{"image": "kathara/frr"})
        router_a2 = self.lab.new_machine("router_a2", **{"image": "kathara/frr"})
        router_b1 = self.lab.new_machine("router_b1", **{"image": "kathara/frr"})
        router_b2 = self.lab.new_machine("router_b2", **{"image": "kathara/frr"})
        router_b3 = self.lab.new_machine("router_b3", **{"image": "kathara/frr"})
        router_c1 = self.lab.new_machine("router_c1", **{"image": "kathara/frr"})
        router_d1 = self.lab.new_machine("router_d1", **{"image": "kathara/frr"})

        pc1 = self.lab.new_machine("pc1", **{"image": "kathara/base"})
        pc2 = self.lab.new_machine("pc2", **{"image": "kathara/base"})

        self.lab.connect_machine_to_link(router_a1.name, "A1_B1")
        self.lab.connect_machine_to_link(router_b1.name, "A1_B1")
        self.lab.connect_machine_to_link(router_a1.name, "A1_B2")
        self.lab.connect_machine_to_link(router_b2.name, "A1_B2")
        self.lab.connect_machine_to_link(router_a1.name, "A1_B3")
        self.lab.connect_machine_to_link(router_b3.name, "A1_B3")

        self.lab.connect_machine_to_link(router_a2.name, "A2_B1")
        self.lab.connect_machine_to_link(router_b1.name, "A2_B1")
        self.lab.connect_machine_to_link(router_a2.name, "A2_B2")
        self.lab.connect_machine_to_link(router_b2.name, "A2_B2")
        self.lab.connect_machine_to_link(router_a2.name, "A2_B3")
        self.lab.connect_machine_to_link(router_b3.name, "A2_B3")

        self.lab.connect_machine_to_link(router_b1.name, "B1_B2")
        self.lab.connect_machine_to_link(router_b2.name, "B1_B2")
        self.lab.connect_machine_to_link(router_b2.name, "B2_B3")
        self.lab.connect_machine_to_link(router_b3.name, "B2_B3")

        self.lab.connect_machine_to_link(router_b1.name, "B1_C1")
        self.lab.connect_machine_to_link(router_c1.name, "B1_C1")
        self.lab.connect_machine_to_link(router_b2.name, "B2_C1")
        self.lab.connect_machine_to_link(router_c1.name, "B2_C1")
        self.lab.connect_machine_to_link(router_b3.name, "B3_C1")
        self.lab.connect_machine_to_link(router_c1.name, "B3_C1")

        self.lab.connect_machine_to_link(router_c1.name, "C1_D1")
        self.lab.connect_machine_to_link(router_d1.name, "C1_D1")

        self.lab.connect_machine_to_link(router_a1.name, "PC1_A1")
        self.lab.connect_machine_to_link(pc1.name, "PC1_A1")

        self.lab.connect_machine_to_link(router_d1.name, "PC2_D1")
        self.lab.connect_machine_to_link(pc2.name, "PC2_D1")

        # Add basic configuration to the machines
        for router in [router_a1, router_a2, router_b1, router_b2, router_b3, router_c1, router_d1]:
            # specific frr conf
            router.copy_directory_from_path(os.path.join(cur_path, f"{router.name}/etc"), "/etc")
            # general conf for frr
            router.create_file_from_path(os.path.join(cur_path, "etc/frr/daemons"), "/etc/frr/daemons")
            router.create_file_from_path(os.path.join(cur_path, "etc/frr/vtysh.conf"), "/etc/frr/vtysh.conf")
            # startup script
            self.lab.create_file_from_path(os.path.join(cur_path, f"{router.name}.startup"), f"{router.name}.startup")

        # PC configuration
        for host in [pc1, pc2]:
            self.lab.create_file_from_path(os.path.join(cur_path, f"{host.name}.startup"), f"{host.name}.startup")


if __name__ == "__main__":
    ibgp_dc_4_level = IBGPDC4Level()
    print("Lab description:", ibgp_dc_4_level.desc)
    print("lab net summary:", ibgp_dc_4_level.net_summary())
    if ibgp_dc_4_level.lab_exists():
        print("Lab exists, undeploying it...")
        ibgp_dc_4_level.undeploy()
        print("Lab undeployed")

    print("Deploying lab...")
    ibgp_dc_4_level.deploy()
    print("Lab deployed")
