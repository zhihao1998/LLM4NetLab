import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from llm4netlab.net_env.base import NetworkEnvBase

LAB_NAME = "ospf_frr_single_area"
cur_path = os.path.dirname(os.path.abspath(__file__))


class OspfFrrSingleArea(NetworkEnvBase):
    def __init__(self):
        super().__init__(os.path.join(cur_path, "metadata.json"))
        self.lab = Lab(LAB_NAME)
        self.name = LAB_NAME
        self.instance = Kathara.get_instance()

        bb0 = self.lab.new_machine("bb0", **{"image": "kathara/frr"})
        bb1 = self.lab.new_machine("bb1", **{"image": "kathara/frr"})
        bb2 = self.lab.new_machine("bb2", **{"image": "kathara/frr"})
        bb3 = self.lab.new_machine("bb3", **{"image": "kathara/frr"})
        bb4 = self.lab.new_machine("bb4", **{"image": "kathara/frr"})

        self.lab.connect_machine_to_link(bb0.name, "A")
        self.lab.connect_machine_to_link(bb1.name, "A")
        self.lab.connect_machine_to_link(bb2.name, "A")

        self.lab.connect_machine_to_link(bb2.name, "B")
        self.lab.connect_machine_to_link(bb3.name, "B")

        self.lab.connect_machine_to_link(bb0.name, "C")
        self.lab.connect_machine_to_link(bb3.name, "C")
        self.lab.connect_machine_to_link(bb4.name, "C")

        self.lab.connect_machine_to_link(bb1.name, "D")
        self.lab.connect_machine_to_link(bb4.name, "D")

        # Add basic configuration to the machines
        for i, bb in enumerate([bb0, bb1, bb2, bb3, bb4]):
            bb.copy_directory_from_path(os.path.join(cur_path, f"bb{i}/etc"), "/etc")
            # to create the startup file, use self.lab instead of host
            self.lab.create_file_from_path(os.path.join(cur_path, f"bb{i}.startup"), f"bb{i}.startup")


if __name__ == "__main__":
    ospf_frr_single = OspfFrrSingleArea()
    if ospf_frr_single.lab_exists():
        print("Lab exists, undeploying it...")
        ospf_frr_single.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # ospf_frr_single.deploy()
    # print("Lab deployed")
