import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from config import BASE_DIR
from llm4netlab.net_env.base import NetworkEnvBase

LAB_NAME = "l2_basic_forwarding"
cur_path = os.path.dirname(os.path.abspath(__file__))


class L2BasicForwarding(NetworkEnvBase):
    def __init__(self):
        # TODO: maybe we do not need a separate metadata.json file, just to dig from the lab
        super().__init__()
        self.lab = Lab(LAB_NAME)
        self.name = LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "A simple L2 forwarding network with 4 hosts and 1 bmv2 switch."

        pc1 = self.lab.new_machine("pc1", **{"image": "kathara/base"})
        pc2 = self.lab.new_machine("pc2", **{"image": "kathara/base"})
        pc3 = self.lab.new_machine("pc3", **{"image": "kathara/base"})
        pc4 = self.lab.new_machine("pc4", **{"image": "kathara/base"})

        s1 = self.lab.new_machine("s1", **{"image": "kathara/p4"})

        self.lab.connect_machine_to_link(pc1.name, "A")
        self.lab.connect_machine_to_link(pc2.name, "B")
        self.lab.connect_machine_to_link(pc3.name, "C")
        self.lab.connect_machine_to_link(pc4.name, "D")

        self.lab.connect_machine_to_link(s1.name, "A")
        self.lab.connect_machine_to_link(s1.name, "B")
        self.lab.connect_machine_to_link(s1.name, "C")
        self.lab.connect_machine_to_link(s1.name, "D")

        # Add basic configuration to the machines
        for i in range(1, 5):
            cmd_list = [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                f"ip link set eth0 address 00:00:0a:00:00:0{i}",
                f"ip addr add 10.0.0.{i}/24 dev eth0",
            ]
            for j in range(1, 5):
                if j != i:
                    cmd_list.append(f"arp -s 10.0.0.{j} 00:00:0a:00:00:0{j}")

            self.lab.create_file_from_list(
                cmd_list,
                f"pc{i}.startup",
            )

        s1.create_file_from_path(
            os.path.join(cur_path, "s1/l2_basic_forwarding.p4"),
            "l2_basic_forwarding.p4",
        )
        s1.create_file_from_path(os.path.join(cur_path, "s1/commands.txt"), "commands.txt")

        # add the sswitch_thrift_API.py file to the Kathara image
        s1.create_file_from_path(
            os.path.join(BASE_DIR, "utils/kathara/sswitch_thrift_API.py"),
            "/usr/local/lib/python3.11/site-packages/sswitch_thrift_API.py",
        )
        s1.create_file_from_path(
            os.path.join(BASE_DIR, "utils/kathara/thrift_API.py"),
            "/usr/local/lib/python3.11/site-packages/thrift_API.py",
        )

        self.lab.create_file_from_list(
            [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                "p4c l2_basic_forwarding.p4",
                "simple_switch -i 1@eth0 -i 2@eth1 -i 3@eth2 -i 4@eth3 --log-console l2_basic_forwarding.json >> sw.log &",
                "while [[ $(pgrep simple_switch) -eq 0 ]]; do sleep 1; done",
                'until simple_switch_CLI <<< "help"; do sleep 1; done',
                "simple_switch_CLI <<< $(cat commands.txt)",
            ],
            "s1.startup",
        )

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
    l2 = L2BasicForwarding()
    print(l2)
    if l2.lab_exists():
        print("Lab exists, undeploying it...")
        l2.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # l2.deploy()
    # print("Lab deployed")
