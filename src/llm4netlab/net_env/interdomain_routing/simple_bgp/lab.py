import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from llm4netlab.config import BASE_DIR
from llm4netlab.net_env.base import NetworkEnvBase

cur_path = os.path.dirname(os.path.abspath(__file__))


class SimpleBGP(NetworkEnvBase):
    LAB_NAME = "simple_bgp"

    def __init__(self, router_num: int = 2, host_num: int = 2):
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "A simple BGP network with two routers and two hosts."

        router1 = self.lab.new_machine("router1", **{"image": "kathara/frr-stress", "cpus": 1})
        router2 = self.lab.new_machine("router2", **{"image": "kathara/frr-stress", "cpus": 1})

        pc1 = self.lab.new_machine("pc1", **{"image": "kathara/base-stress"})
        pc2 = self.lab.new_machine("pc2", **{"image": "kathara/base-stress"})

        self.lab.connect_machine_to_link(router1.name, "A")
        self.lab.connect_machine_to_link(router2.name, "A")

        self.lab.connect_machine_to_link(router1.name, "B")
        self.lab.connect_machine_to_link(pc1.name, "B")

        self.lab.connect_machine_to_link(router2.name, "C")
        self.lab.connect_machine_to_link(pc2.name, "C")

        # Add basic configuration to the machines
        for i, router in enumerate([router1, router2], start=1):
            router.copy_directory_from_path(os.path.join(cur_path, f"router{i}/etc"), "/etc")
            router.create_file_from_path(
                os.path.join(BASE_DIR, "src/llm4netlab/net_env/utils/bgp/daemons"), "/etc/frr/daemons"
            )
            router.create_file_from_path(
                os.path.join(BASE_DIR, "src/llm4netlab/net_env/utils/bgp/vtysh.conf"), "/etc/frr/vtysh.conf"
            )
            # to create the startup file, use self.lab instead of host
            self.lab.create_file_from_path(os.path.join(cur_path, f"router{i}.startup"), f"router{i}.startup")

        for i, host in enumerate([pc1, pc2], start=1):
            self.lab.create_file_from_path(os.path.join(cur_path, f"pc{i}.startup"), f"pc{i}.startup")

        # load machines
        self.load_machines()


if __name__ == "__main__":
    simple_bgp = SimpleBGP()
    print(simple_bgp)
    if simple_bgp.lab_exists():
        print("Lab exists, undeploying it...")
        simple_bgp.undeploy()
        # simple_bgp.instance.undeploy_lab(lab_name=simple_bgp.lab.name, selected_machines=["router1"])
        print("Lab undeployed")

    # print("Deploying lab...")
    # simple_bgp.deploy()
    # print("Lab deployed")
