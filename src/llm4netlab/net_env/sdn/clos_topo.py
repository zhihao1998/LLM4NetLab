import os
import textwrap
from ipaddress import IPv4Interface, IPv4Network
from typing import Literal

from Kathara.manager.Kathara import Kathara, Machine
from Kathara.model.Lab import Lab

from llm4netlab.net_env.base import NetworkEnvBase

cur_path = os.path.dirname(os.path.abspath(__file__))


# P2P links use 172.16.0.0/16 with /31 per link.
def assign_p2p_ips(subnet: IPv4Network):
    base = subnet.network_address
    ip0 = IPv4Interface(f"{base}/31")
    ip1 = IPv4Interface(f"{base + 1}/31")
    return str(ip0), str(ip1)


class SwitchMeta:
    def __init__(self, name, machine: Machine, eth_index, cmd_list):
        self.name = name
        self.machine = machine
        self.eth_index = eth_index
        self.cmd_list = cmd_list


class HostMeta:
    def __init__(self, name, machine: Machine, eth_index, cmd_list):
        self.name = name
        self.machine = machine
        self.eth_index = eth_index
        self.cmd_list = cmd_list
        self.ip_address = None


class SDNClos(NetworkEnvBase):
    LAB_NAME = "sdn_clos"
    TOPO_LEVEL = "medium"
    TOPO_SIZE = ["s", "m", "l"]
    TAGS = ["link", "sdn", "host", "mac", "arp", "icmp"]

    def __init__(self, topo_size_level: Literal["s", "m", "l"] = "s"):
        super().__init__()
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.topo_size_level = topo_size_level

        # Level s:  1 spine, 4 leaf, 2 hosts per leaf
        # Level m:  2 spine, 8 leaf, 2 hosts per leaf
        # Level l:  4 spine, 16 leaf, 2 hosts per leaf
        if topo_size_level == "s":
            SPINE_NUM, LEAF_NUM, HOST_PER_LEAF = 1, 4, 2
        elif topo_size_level == "m":
            SPINE_NUM, LEAF_NUM, HOST_PER_LEAF = 2, 8, 2
        elif topo_size_level == "l":
            SPINE_NUM, LEAF_NUM, HOST_PER_LEAF = 4, 16, 2
        else:
            raise ValueError("topo_size_level should be s, m, or l.")

        self.desc = textwrap.dedent("""\
            This experiment uses a scalable SDN spine–leaf topology whose size depends on the selected topo_size_level.
            Each leaf switch connects to all spine switches using point-to-point links.
            Each leaf switch connects to two hosts belong to the same subnet 10.0.0.0/24.
            All switches also join a management network 20.0.0.0/24.
            The SDN controller resides at 20.0.0.100 and manages all switches via OpenFlow.""")

        # ---------- create leaf and spine switches ----------
        spine_switches = []
        leaf_switches = []

        # Spine
        for i in range(SPINE_NUM):
            switch_name = f"spine_{i + 1}"
            switch = self.lab.new_machine(switch_name, **{"image": "kathara/sdn", "cpus": 0.5, "mem": "256m"})
            switch_meta = SwitchMeta(
                name=switch_name,
                machine=switch,
                eth_index=0,
                cmd_list=[],
            )
            spine_switches.append(switch_meta)

        # Leaf
        for i in range(LEAF_NUM):
            switch_name = f"leaf_{i + 1}"
            switch = self.lab.new_machine(switch_name, **{"image": "kathara/sdn", "cpus": 0.5, "mem": "256m"})
            switch_meta = SwitchMeta(
                name=switch_name,
                machine=switch,
                eth_index=0,
                cmd_list=[],
            )
            leaf_switches.append(switch_meta)

        tot_switch_list = spine_switches + leaf_switches

        # ---------- Create Host ----------
        tot_host_list = []
        for leaf_id in range(LEAF_NUM):
            for host_id in range(HOST_PER_LEAF):
                host_name = f"host_{leaf_id + 1}_{host_id + 1}"
                host_machine = self.lab.new_machine(
                    host_name, **{"image": "kathara/base-stress", "cpus": 0.5, "mem": "256m"}
                )
                host_meta = HostMeta(
                    name=host_name,
                    machine=host_machine,
                    eth_index=0,
                    cmd_list=[],
                )
                tot_host_list.append(host_meta)

        # ---------- Controller ----------
        controller = self.lab.new_machine(
            "controller", **{"image": "kathara/ryu-stress", "cpus": 0.5, "mem": "256m", "bridged": True}
        )

        # ---------- Switch initialize ----------
        for switch_meta in tot_switch_list:
            switch_meta.cmd_list.append("/usr/share/openvswitch/scripts/ovs-ctl --system-id=random start")
            switch_meta.cmd_list.append(f"ovs-vsctl add-br {switch_meta.name}")
            switch_meta.cmd_list.append(f"ovs-vsctl set-fail-mode {switch_meta.name} secure")

        # ---------- Host-leaf connection ----------
        host_network = IPv4Network("10.0.0.0/24")
        host_pool = host_network.hosts()
        for leaf_idx, leaf_switch in enumerate(leaf_switches, start=1):
            # find hosts belong to this leaf
            leaf_hosts = [h for h in tot_host_list if h.name.startswith(f"host_{leaf_idx}_")]

            for host_meta in leaf_hosts:
                link_name = f"{host_meta.name}_{leaf_switch.name}"

                self.lab.connect_machine_to_link(host_meta.machine.name, link_name)
                self.lab.connect_machine_to_link(leaf_switch.machine.name, link_name)

                # eth<host_meta.eth_index>
                host_ip = str(next(host_pool))
                host_meta.ip_address = host_ip
                host_meta.cmd_list.append(f"ip addr add {host_ip}/24 dev eth{host_meta.eth_index}")
                host_meta.cmd_list.append(f"ip link set eth{host_meta.eth_index} up")
                host_meta.ip_address = host_ip
                host_meta.eth_index += 1

                # OVS port on leaf switch
                leaf_switch.cmd_list.append(f"ovs-vsctl add-port {leaf_switch.name} eth{leaf_switch.eth_index}")
                leaf_switch.cmd_list.append(f"ip link set eth{leaf_switch.eth_index} up")
                leaf_switch.eth_index += 1

        # ---------- Spine-Leaf mesh  ----------
        for spine in spine_switches:
            for leaf in leaf_switches:
                link_name = f"{spine.name}_{leaf.name}"

                self.lab.connect_machine_to_link(spine.machine.name, link_name)
                self.lab.connect_machine_to_link(leaf.machine.name, link_name)

                # Spine
                spine.cmd_list.append(f"ovs-vsctl add-port {spine.name} eth{spine.eth_index}")
                spine.eth_index += 1

                # Leaf
                leaf.cmd_list.append(f"ovs-vsctl add-port {leaf.name} eth{leaf.eth_index}")
                leaf.eth_index += 1

        # ---------- Control plane ----------
        infra_network = IPv4Network("20.0.0.0/24").hosts()
        controller_ip = "20.0.0.100"

        # all switches connect to controller
        for switch_meta in tot_switch_list:
            switch_ip = str(next(infra_network))

            self.lab.connect_machine_to_link(switch_meta.machine.name, "switch_controller")

            switch_meta.cmd_list.append(f"ip addr add {switch_ip}/24 dev eth{switch_meta.eth_index}")
            switch_meta.cmd_list.append(f"ip link set eth{switch_meta.eth_index} up")
            switch_meta.cmd_list.append(f"ovs-vsctl set-controller {switch_meta.name} tcp:{controller_ip}:6633")
            switch_meta.eth_index += 1

        self.lab.connect_machine_to_link(controller.name, "switch_controller")

        # ---------- Controller start script ----------
        self.lab.create_file_from_list(
            [
                "ip addr add 20.0.0.100/24 dev eth0",
                "ip link set eth0 up",
                "ryu-manager ryu.app.simple_switch &",
            ],
            f"{controller.name}.startup",
        )

        # ---------- Switch start script ----------
        for switch_meta in tot_switch_list:
            self.lab.create_file_from_list(
                switch_meta.cmd_list,
                f"{switch_meta.machine.name}.startup",
            )

        # ---------- Host start script ----------
        for host_meta in tot_host_list:
            self.lab.create_file_from_list(
                host_meta.cmd_list,
                f"{host_meta.machine.name}.startup",
            )

        self.load_machines()


if __name__ == "__main__":
    lab = SDNClos(topo_size_level="m")
    print("Lab description:", lab.desc)
    print("lab net summary:", lab.get_info())
    if lab.lab_exists():
        print("Lab exists, undeploying it...")
        lab.undeploy()
        print("Lab undeployed")

    # lab.deploy()
    # print("Lab deployed")
