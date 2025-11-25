import os
from collections import defaultdict
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


class RIPSmallInternetVPN(NetworkEnvBase):
    LAB_NAME = "rip_small_internet_vpn"

    def __init__(self):
        super().__init__()
        self.lab = Lab(self.LAB_NAME)
        self.name = self.LAB_NAME
        self.instance = Kathara.get_instance()
        self.desc = "An stub RIP network with 5 routers, 4 pcs and 1 server. R5 is the gateway to the internet."

        host_num = 4
        server_num = 2

        # addresses between routers
        infra_pool = list(IPv4Network("172.16.0.0/16").subnets(new_prefix=31))

        # internal routers
        internal_router_list: list[RIPRouterMeta] = []
        for range_idx in range(1, 5):
            router_name = f"router{range_idx}"
            router_machine = self.lab.new_machine(router_name, **{"image": "kathara/frr", "cpu": 1, "mem": "512M"})
            router_meta = RIPRouterMeta(
                name=router_name,
                machine=router_machine,
                eth_index=0,
                cmd_list=[],
            )
            internal_router_list.append(router_meta)

        # internal hosts
        tot_host_list: list[HostMeta] = []
        for host_idx in range(1, host_num + 1):
            host_name = f"host_{host_idx}"
            host_machine = self.lab.new_machine(host_name, **{"image": "kathara/wireguard", "cpu": 1, "mem": "512M"})
            host_meta = HostMeta(
                name=host_name,
                machine=host_machine,
                eth_index=0,
                cmd_list=[],
            )
            tot_host_list.append(host_meta)

        # add the internet gateway router
        gateway_router_machine = self.lab.new_machine(
            "gateway_router", **{"image": "kathara/frr", "cpu": 1, "mem": "512M"}
        )
        gateway_router_meta = RIPRouterMeta(
            name="gateway_router",
            machine=gateway_router_machine,
            eth_index=0,
            cmd_list=[],
        )

        # add two routers for the external services
        external_zone_num = 1
        external_routers: list[RIPRouterMeta] = []
        for i in range(1, external_zone_num + 1):
            router_name = f"external_router_{i}"
            router_machine = self.lab.new_machine(router_name, **{"image": "kathara/frr", "cpu": 1, "mem": "512M"})
            router_meta = RIPRouterMeta(
                name=router_name,
                machine=router_machine,
                eth_index=0,
                cmd_list=[],
            )
            external_routers.append(router_meta)

        # external web servers for each external router (zone)
        external_server_dict = defaultdict(list)
        for i in range(1, external_zone_num + 1):
            for server_idx in range(1, server_num + 1):
                server_name = f"web_server_{i}_{server_idx}"
                server_machine = self.lab.new_machine(
                    server_name, **{"image": "kathara/wireguard", "cpu": 1, "mem": "512M"}
                )
                server_meta = HostMeta(
                    name=server_name,
                    machine=server_machine,
                    eth_index=0,
                    cmd_list=[],
                )
                external_server_dict[f"external_router_{i}"].append(server_meta)

        # add vpn server per external zone
        tot_vpn_dict = {}
        for i in range(1, external_zone_num + 1):
            vpn_server_name = f"vpn_server_{i}"
            vpn_server_machine = self.lab.new_machine(
                vpn_server_name, **{"image": "kathara/wireguard", "cpu": 1, "mem": "512M"}
            )
            vpn_server_meta = HostMeta(
                name=vpn_server_name,
                machine=vpn_server_machine,
                eth_index=0,
                cmd_list=[],
            )
            tot_vpn_dict[f"external_router_{i}"] = vpn_server_meta

        # connect routers to each other
        for r_a, r_b in [
            (internal_router_list[0], internal_router_list[1]),
            (internal_router_list[0], internal_router_list[2]),
            (internal_router_list[0], internal_router_list[3]),
            (internal_router_list[1], internal_router_list[2]),
            (internal_router_list[2], internal_router_list[3]),
            (internal_router_list[3], gateway_router_meta),
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
        for i in range(host_num):
            router_meta = internal_router_list[i]
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

        # connect external routers to gateway router
        for ext_router in external_routers:
            link_name = f"{ext_router.machine.name}_{gateway_router_meta.machine.name}"
            self.lab.connect_machine_to_link(ext_router.machine.name, link_name)
            self.lab.connect_machine_to_link(gateway_router_meta.machine.name, link_name)

            subnet = infra_pool.pop(0)
            a_ip, b_ip = assign_p2p_ips(subnet)
            ext_router.cmd_list.append(f"ip addr add {a_ip} dev eth{ext_router.eth_index}")
            ext_router.eth_index += 1
            gateway_router_meta.cmd_list.append(f"ip addr add {b_ip} dev eth{gateway_router_meta.eth_index}")
            gateway_router_meta.eth_index += 1

        # connect web servers to external routers
        for ext_idx, ext_router in enumerate(external_routers):
            # add a bridge at the external router to connect servers
            ext_router.cmd_list.append("brctl addbr br0")
            ext_router.cmd_list.append("ip link set dev br0 up")

            zone_network = IPv4Network(f"20.0.{ext_idx}.0/24")
            ext_router.host_network = zone_network
            zone_ip_base = zone_network.hosts()
            ext_router_ip = str(IPv4Interface(f"{next(zone_ip_base)}/24"))
            ext_router.cmd_list.append(f"ip addr add {ext_router_ip} dev br0")

            for server_meta in external_server_dict[ext_router.name]:
                # connect server to the bridge
                self.lab.connect_machine_to_link(
                    server_meta.machine.name, f"{ext_router.machine.name}_{server_meta.machine.name}"
                )
                self.lab.connect_machine_to_link(
                    ext_router.machine.name, f"{ext_router.machine.name}_{server_meta.machine.name}"
                )
                ext_router.cmd_list.append(f"brctl addif br0 eth{ext_router.eth_index}")
                ext_router.eth_index += 1
                server_ip = str(IPv4Interface(f"{next(zone_ip_base)}/24"))
                server_meta.cmd_list.append(f"ip addr add {server_ip} dev eth{server_meta.eth_index}")
                server_meta.cmd_list.append(f"ip route add default via {ext_router_ip.split('/')[0]}")
                server_meta.eth_index += 1

            # connect vpn servers to external routers
            for vpn_server_meta in [tot_vpn_dict[ext_router.name]]:
                self.lab.connect_machine_to_link(
                    vpn_server_meta.machine.name, f"{ext_router.machine.name}_{vpn_server_meta.machine.name}"
                )
                self.lab.connect_machine_to_link(
                    ext_router.machine.name, f"{ext_router.machine.name}_{vpn_server_meta.machine.name}"
                )
                ext_router.cmd_list.append(f"brctl addif br0 eth{ext_router.eth_index}")
                ext_router.eth_index += 1
                vpn_server_ip = str(IPv4Interface(f"{next(zone_ip_base)}/24"))
                vpn_server_meta.cmd_list.append(f"ip addr add {vpn_server_ip} dev eth{vpn_server_meta.eth_index}")
                vpn_server_meta.cmd_list.append(f"ip route add default via {ext_router_ip.split('/')[0]}")
                vpn_server_meta.eth_index += 1
                vpn_server_meta.ip_address = vpn_server_ip.split("/")[0]

        # Add basic configuration to the routers
        for router_meta in internal_router_list + [gateway_router_meta] + external_routers:
            # general conf for frr
            router_meta.machine.create_file_from_path(
                os.path.join(BASE_DIR, "src/llm4netlab/net_env/utils/rip/daemons"), "/etc/frr/daemons"
            )
            router_meta.machine.create_file_from_path(
                os.path.join(BASE_DIR, "src/llm4netlab/net_env/utils/rip/vtysh.conf"), "/etc/frr/vtysh.conf"
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
            if host.name == "host_1":
                # set default vpn client config for host_1
                host.machine.copy_directory_from_path(
                    os.path.join(cur_path, "confs", "host_1"),
                    "/",
                )
                host.cmd_list.append("wg-quick up wg0")

            self.lab.create_file_from_list(
                host.cmd_list,
                f"{host.machine.name}.startup",
            )

        # Add basic configuration to external servers
        for ext_router in external_routers:
            # add vpn private subnet
            vpn_server_meta.machine.copy_directory_from_path(
                os.path.join(cur_path, "confs", f"{vpn_server_meta.name}"),
                "/",
            )
            vpn_server_meta = tot_vpn_dict[ext_router.name]
            vpn_server_meta.cmd_list.append("wg-quick up wg0")
            self.lab.create_file_from_list(
                vpn_server_meta.cmd_list,
                f"{vpn_server_meta.machine.name}.startup",
            )

            for server_meta in external_server_dict[ext_router.name]:
                server_meta.machine.copy_directory_from_path(
                    os.path.join(cur_path, "confs", f"{server_meta.name}"), "/"
                )
                server_meta.cmd_list.append("wg-quick up wg0")
                server_meta.cmd_list.append("service apache2 start")
                self.lab.create_file_from_list(
                    server_meta.cmd_list,
                    f"{server_meta.machine.name}.startup",
                )


if __name__ == "__main__":
    rip_small_internet = RIPSmallInternetVPN()
    print("Lab description:", rip_small_internet.desc)
    print("lab net summary:", rip_small_internet.get_info())
    if rip_small_internet.lab_exists():
        print("Lab exists, undeploying it...")
        rip_small_internet.undeploy()
        print("Lab undeployed")

    # print("Deploying lab...")
    # rip_small_internet.deploy()
    # print("Lab deployed")
