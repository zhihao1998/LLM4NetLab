import os
from ipaddress import IPv4Interface, IPv4Network

from Kathara.manager.Kathara import Kathara, Machine
from Kathara.model.Lab import Lab

from llm4netlab.config import BASE_DIR
from llm4netlab.net_env.base import NetworkEnvBase

cur_path = os.path.dirname(os.path.abspath(__file__))


class RIPRouterMeta:
    def __init__(self, name, machine: Machine, eth_index, cmd_list):
        self.name = name
        self.machine = machine
        self.eth_index = eth_index
        self.cmd_list = cmd_list
        self.frr_config = ""
        self.host_network = None


class HostMeta:
    def __init__(self, name, machine: Machine, eth_index, cmd_list):
        self.name = name
        self.machine = machine
        self.eth_index = eth_index
        self.cmd_list = cmd_list


def assign_p2p_ips(subnet):
    base = subnet.network_address
    ip0 = IPv4Interface(f"{base}/31")
    ip1 = IPv4Interface(f"{base + 1}/31")
    return str(ip0), str(ip1)


FRR_BASE_TEMPLATE_RIP = """
!
! FRRouting configuration file
!
!
!  RIP CONFIGURATION
!
router rip
network 172.16.0.0/16
network {network}
redistribute static
!
log file /var/log/frr/frr.log
"""


class RIPSmallInternet(NetworkEnvBase):
    LAB_NAME = "rip_small_internet"

    def __init__(self):
        super().__init__()
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "An stub RIP network with 5 routers, 4 pcs and 1 server. R5 is the gateway to the internet."

        # addresses between routers
        infra_pool = list(IPv4Network("172.16.0.0/16").subnets(new_prefix=31))

        tot_router_list: list[RIPRouterMeta] = []
        for range_idx in range(1, 5):
            router_name = f"router{range_idx}"
            router_machine = self.lab.new_machine(router_name, **{"image": "kathara/frr"})
            router_meta = RIPRouterMeta(
                name=router_name,
                machine=router_machine,
                eth_index=0,
                cmd_list=[],
            )
            tot_router_list.append(router_meta)
        # add the internet gateway router
        router_name = "gateway_router"
        router_machine = self.lab.new_machine(router_name, **{"image": "kathara/frr"})
        router_meta = RIPRouterMeta(
            name=router_name,
            machine=router_machine,
            eth_index=0,
            cmd_list=[],
        )
        tot_router_list.append(router_meta)

        tot_host_list: list[HostMeta] = []
        for pc_idx in range(1, 5):
            pc_name = f"pc{pc_idx}"
            pc_machine = self.lab.new_machine(pc_name, **{"image": "kathara/base"})
            pc_meta = HostMeta(
                name=pc_name,
                machine=pc_machine,
                eth_index=0,
                cmd_list=[],
            )
            tot_host_list.append(pc_meta)
        server_meta = HostMeta(
            name="server",
            machine=self.lab.new_machine("server", **{"image": "kathara/base"}),
            eth_index=0,
            cmd_list=[],
        )
        tot_host_list.append(server_meta)

        for r_a, r_b in [
            (tot_router_list[0], tot_router_list[1]),
            (tot_router_list[0], tot_router_list[2]),
            (tot_router_list[0], tot_router_list[3]),
            (tot_router_list[1], tot_router_list[2]),
            (tot_router_list[2], tot_router_list[3]),
            (tot_router_list[3], tot_router_list[4]),
        ]:
            link_name = f"{r_a.machine.name}_{r_b.machine.name}"
            self.lab.connect_machine_to_link(r_a.machine.name, link_name)
            self.lab.connect_machine_to_link(r_b.machine.name, link_name)

            subnet = infra_pool.pop(0)
            a_ip, b_ip = assign_p2p_ips(subnet)
            r_a.cmd_list.append(f"ip addr add {a_ip} dev eth{r_a.eth_index}")
            r_a.eth_index += 1
            r_b.cmd_list.append(f"ip addr add {b_ip} dev eth{r_b.eth_index}")
            r_b.eth_index += 1

        # connect hosts to routers
        for i in range(5):
            router_meta = tot_router_list[i]
            host_meta = tot_host_list[i]
            self.lab.connect_machine_to_link(
                router_meta.machine.name, f"{router_meta.machine.name}_{host_meta.machine.name}"
            )
            self.lab.connect_machine_to_link(
                host_meta.machine.name, f"{router_meta.machine.name}_{host_meta.machine.name}"
            )

            subnet = IPv4Network(f"10.0.{i}.0/24")
            router_ip = str(IPv4Interface(f"{subnet.network_address + 1}/24"))
            pc_ip = str(IPv4Interface(f"{subnet.network_address + 2}/24"))
            router_meta.cmd_list.append(f"ip addr add {router_ip} dev eth{router_meta.eth_index}")
            router_meta.eth_index += 1
            router_meta.host_network = subnet

            host_meta.cmd_list.append(f"ip addr add {pc_ip} dev eth{host_meta.eth_index}")
            host_meta.eth_index += 1
            host_meta.cmd_list.append(f"ip route add default via {router_ip.split('/')[0]}")

        # Add basic configuration to the routers
        for router_meta in tot_router_list:
            # general conf for frr
            router_meta.machine.create_file_from_path(
                os.path.join(BASE_DIR, "llm4netlab/net_env/utils/rip/daemons"), "/etc/frr/daemons"
            )
            router_meta.machine.create_file_from_path(
                os.path.join(BASE_DIR, "llm4netlab/net_env/utils/rip/vtysh.conf"), "/etc/frr/vtysh.conf"
            )
            router_meta.frr_config = FRR_BASE_TEMPLATE_RIP.format(
                network=str(router_meta.host_network),
            )
            router_meta.machine.create_file_from_string(router_meta.frr_config, "/etc/frr/frr.conf")

            # startup file
            router_meta.cmd_list.append("service frr start")
            self.lab.create_file_from_list(
                router_meta.cmd_list,
                f"{router_meta.machine.name}.startup",
            )

        # Add basic configuration to hosts
        for host in tot_host_list:
            if host.name == "server":
                # server setup: start a simple http server
                host.cmd_list.append("nohup python3 -m http.server 80 &")

            self.lab.create_file_from_list(
                host.cmd_list,
                f"{host.machine.name}.startup",
            )


if __name__ == "__main__":
    rip_small_internet = RIPSmallInternet()
    print("Lab description:", rip_small_internet.desc)
    print("lab net summary:", rip_small_internet.net_summary())
    if rip_small_internet.lab_exists():
        print("Lab exists, undeploying it...")
        rip_small_internet.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # rip_small_internet.deploy()
    # print("Lab deployed")
