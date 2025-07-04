import os

from Kathara.manager.Kathara import Kathara
from Kathara.model.Lab import Lab

from config import BASE_DIR
from llm4netlab.net_env.base import NetworkEnvBase

LAB_NAME = "simple_bmv2"
cur_path = os.path.dirname(os.path.abspath(__file__))


class SimpleTC(NetworkEnvBase):
    def __init__(self):
        super().__init__(os.path.join(cur_path, "metadata.json"))
        self.lab = Lab(LAB_NAME)
        self.name = LAB_NAME
        self.instance = Kathara.get_instance()

        pc1 = self.lab.new_machine("pc1", **{"image": "kathara/base"})
        pc2 = self.lab.new_machine("pc2", **{"image": "kathara/base"})
        pc3 = self.lab.new_machine("pc3", **{"image": "kathara/base"})

        s1 = self.lab.new_machine("s1", **{"image": "kathara/p4"})
        s2 = self.lab.new_machine("s2", **{"image": "kathara/p4"})
        s3 = self.lab.new_machine("s3", **{"image": "kathara/p4"})
        s4 = self.lab.new_machine("s4", **{"image": "kathara/p4"})

        self.lab.connect_machine_to_link(pc1.name, "A", 0)
        self.lab.connect_machine_to_link(s1.name, "A", 0)

        self.lab.connect_machine_to_link(s1.name, "B", 1)
        self.lab.connect_machine_to_link(s2.name, "B", 0)

        self.lab.connect_machine_to_link(s1.name, "C", 2)
        self.lab.connect_machine_to_link(s3.name, "C", 0)

        self.lab.connect_machine_to_link(s2.name, "D", 1)
        self.lab.connect_machine_to_link(s4.name, "D", 0)

        self.lab.connect_machine_to_link(s3.name, "E", 1)
        self.lab.connect_machine_to_link(s4.name, "E", 1)

        self.lab.connect_machine_to_link(pc2.name, "F", 0)
        self.lab.connect_machine_to_link(s4.name, "F", 2)

        self.lab.connect_machine_to_link(pc3.name, "G", 0)
        self.lab.connect_machine_to_link(s4.name, "G", 3)

        # Add basic configuration to the machines
        for i in range(1, 4):
            cmd_list = [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                f"ip link set eth0 address 00:00:0a:00:00:0{i}",
                f"ip addr add 10.0.0.{i}/24 dev eth0",
            ]
            for j in range(1, 4):
                if j != i:
                    cmd_list.append(f"arp -s 10.0.0.{j} 00:00:0a:00:00:0{j}")

            self.lab.create_file_from_list(
                cmd_list,
                f"pc{i}.startup",
            )

        for i, s_i in enumerate([s1, s2, s3, s4], start=1):
            s_i.create_file_from_path(
                os.path.join(cur_path, "p4_src/l2_basic_forwarding_counter.p4"),
                "l2_basic_forwarding_counter.p4",
            )
            s_i.create_file_from_path(os.path.join(cur_path, f"cmds/s{i}.txt"), "commands.txt")

            # add the sswitch_thrift_API.py file to the Kathara image
            s_i.create_file_from_path(
                os.path.join(BASE_DIR, "utils/kathara/sswitch_thrift_API.py"),
                "/usr/local/lib/python3.11/site-packages/sswitch_thrift_API.py",
            )
            s_i.create_file_from_path(
                os.path.join(BASE_DIR, "utils/kathara/thrift_API.py"),
                "/usr/local/lib/python3.11/site-packages/thrift_API.py",
            )

        self.lab.create_file_from_list(
            [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                "p4c l2_basic_forwarding_counter.p4",
                "simple_switch -i 1@eth0 -i 2@eth1 -i 3@eth2 --log-console l2_basic_forwarding_counter.json >> sw.log &",
                "while [[ $(pgrep simple_switch) -eq 0 ]]; do sleep 1; done",
                'until simple_switch_CLI <<< "help"; do sleep 1; done',
                "simple_switch_CLI <<< $(cat commands.txt)",
            ],
            "s1.startup",
        )

        self.lab.create_file_from_list(
            [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                "p4c l2_basic_forwarding_counter.p4",
                "simple_switch -i 1@eth0 -i 2@eth1 --log-console l2_basic_forwarding_counter.json >> sw.log &",
                "while [[ $(pgrep simple_switch) -eq 0 ]]; do sleep 1; done",
                'until simple_switch_CLI <<< "help"; do sleep 1; done',
                "simple_switch_CLI <<< $(cat commands.txt)",
            ],
            "s2.startup",
        )

        self.lab.create_file_from_list(
            [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                "p4c l2_basic_forwarding_counter.p4",
                "simple_switch -i 1@eth0 -i 2@eth1 --log-console l2_basic_forwarding_counter.json >> sw.log &",
                "while [[ $(pgrep simple_switch) -eq 0 ]]; do sleep 1; done",
                'until simple_switch_CLI <<< "help"; do sleep 1; done',
                "simple_switch_CLI <<< $(cat commands.txt)",
            ],
            "s3.startup",
        )

        self.lab.create_file_from_list(
            [
                "sysctl net.ipv4.conf.all.arp_ignore=8",
                "sysctl net.ipv4.conf.default.arp_ignore=8",
                "sysctl net.ipv4.conf.all.arp_announce=8",
                "sysctl net.ipv4.conf.default.arp_announce=8",
                "p4c l2_basic_forwarding_counter.p4",
                "simple_switch -i 1@eth0 -i 2@eth1 -i 3@eth2 -i 4@eth3 --log-console l2_basic_forwarding_counter.json >> sw.log &",
                "while [[ $(pgrep simple_switch) -eq 0 ]]; do sleep 1; done",
                'until simple_switch_CLI <<< "help"; do sleep 1; done',
                "simple_switch_CLI <<< $(cat commands.txt)",
            ],
            "s4.startup",
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
    l2 = SimpleTC()
    print(l2.net_summary())
    if l2.lab_exists():
        print("Lab exists, undeploying it...")
        l2.undeploy()
        print("Lab undeployed")

    print("Deploying lab...")
    l2.deploy()
    print("Lab deployed")
