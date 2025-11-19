import logging
import os

import docker

from llm4netlab.config import BASE_DIR
from llm4netlab.service.kathara import KatharaAPIALL

""" Fault injector for Kathara """


class FaultInjectorBase:
    def __init__(self, lab_name: str):
        self.kathara_api = KatharaAPIALL(lab_name)
        self.logger = logging.getLogger(__name__)

    def inject_intf_down(self, host_name: str, intf_name: str):
        """Bring down a specific interface of a host."""
        self.kathara_api.intf_on_off(host_name=host_name, interface=intf_name, state="down")
        self.logger.info(f"Injected interface down on {host_name}:{intf_name}")

    def recover_intf_down(self, host_name: str, intf_name: str):
        """Recover from an interface down by enabling the interface."""
        self.kathara_api.intf_on_off(host_name=host_name, interface=intf_name, state="up")
        self.logger.info(f"Recovered interface down on {host_name}:{intf_name}")

    def inject_link_flap(self, host_name: str, intf_name: str, down_time: int = 1, up_time: int = 1):
        """Inject link flap on a specific interface of a host."""
        with open(os.path.join(BASE_DIR, "src/llm4netlab/generator/fault/utils/link_flap.sh"), "r") as f:
            script = f.read()
        write_cmd = f"cat <<'EOF' > /tmp/link_flap.sh\n{script}\nEOF\nchmod +x /tmp/link_flap.sh"
        self.kathara_api.exec_cmd(host_name, write_cmd)

        # kill the previous link flap process if any
        self.kathara_api.exec_cmd(
            host_name, "if [ -f /tmp/link_flap.pid ]; then kill $(cat /tmp/link_flap.pid) 2>/dev/null; fi"
        )

        # start the link flap script
        start_cmd = (
            f"nohup /tmp/link_flap.sh {intf_name} {down_time} {up_time} "
            f"> /tmp/link_flap_{intf_name}.log 2>&1 & echo $! > /tmp/link_flap.pid"
        )
        self.kathara_api.exec_cmd(host_name, start_cmd)

        self.logger.info(f"Injected link flap on {host_name}:{intf_name} (down_time={down_time}, up_time={up_time})")

    def recover_link_flap(self, host_name: str, intf_name: str):
        # kill process & restore interface
        stop_cmd = (
            "if [ -f /tmp/link_flap.pid ]; then "
            "  kill $(cat /tmp/link_flap.pid) 2>/dev/null || true; "
            "  rm -f /tmp/link_flap.pid; "
            f"  ip link set {intf_name} up; "
            "fi"
        )
        self.kathara_api.exec_cmd(host_name, stop_cmd)
        self.logger.info(f"Stopped link flap on {host_name}:{intf_name}")

    def inject_link_detach(self, host_name: str, link_name: str):
        """Detach a specific interface of a host.
        Note: link_name is the name of the collision domain that the interface is connected to.
        """
        machine_obj = self.kathara_api.lab.get_machine(host_name)
        link_obj = self.kathara_api.lab.get_link(link_name)
        self.kathara_api.instance.disconnect_machine_from_link(machine=machine_obj, link=link_obj)
        self.logger.info(f"Injected link detach on {host_name}:{link_name}")

    def recover_link_detach(self, host_name: str, link_name: str):
        """Recover from a link detach by re-attaching the interface to the link.
        Note: link_name is the name of the collision domain that the interface is connected to.
        TODO: Fix, not working
        """
        # machine_obj = self.kathara_api.lab.get_machine(host_name)
        # link_obj = self.kathara_api.lab.get_link(link_name)
        # machine_obj.remove_interface(link_obj)
        # machine_obj.add_interface(link_obj)
        # self.kathara_api.instance.connect_machine_to_link(machine=machine_obj, link=link_obj)
        # self.logger.info(f"Recovered link detach on {host_name}:{link_name}")
        pass

    def inject_host_down(self, host_name: str):
        """Inject a fault by stopping a host."""
        docker_client = docker.from_env()
        container_name = docker_client.containers.list(filters={"name": f"{host_name}"})[0]
        container_name.pause()
        self.logger.info(f"Injected host down fault on {host_name}.")

    def recover_host_down(self, host_name: str):
        """Recover from a fault by starting a host."""
        docker_client = docker.from_env()
        container_name = docker_client.containers.list(filters={"name": f"{host_name}"})[0]
        container_name.unpause()
        self.logger.info(f"Recovered host down fault on {host_name}.")

    def inject_fragmentation_disabled(self, host_name: str, mtu: int = 100):
        self.kathara_api.exec_cmd(host_name, f"iptables -A OUTPUT -m length --length {mtu}:65535 -j DROP")
        self.logger.info(f"Injected fragmentation disabled on {host_name} with MTU {mtu}.")

    def recover_fragmentation_disabled(self, host_name: str):
        self.kathara_api.exec_cmd(host_name, "iptables -F OUTPUT")
        self.logger.info(f"Recovered fragmentation disabled on {host_name}.")

    def inject_acl_rule(self, host_name: str, rule: str, table_name: str = "filter"):
        """Inject an ACL rule into a specific host."""
        self.kathara_api.nft_add_table(host_name=host_name, table_name=table_name)
        for chain_name in ["input", "forward", "output"]:
            self.kathara_api.nft_add_chain(
                host_name=host_name,
                table=table_name,
                chain=chain_name,
                hook=chain_name,
                type="filter",
                policy="accept",
            )
            self.kathara_api.nft_add_rule(
                host_name=host_name,
                table=table_name,
                chain=chain_name,
                rule=rule,
            )
        self.logger.info(f"Injected ACL rule on {host_name}: {rule}")

    def recover_acl_rule(self, host_name: str, table_name: str = "filter"):
        """Recover from an ACL rule by deleting the filter table."""
        self.kathara_api.nft_delete_table(host_name=host_name, table_name=table_name)
        self.logger.info(f"Recovered ACL rules on {host_name} by deleting table {table_name}.")

    def inject_service_down(self, host_name: str, service_name: str):
        """Inject a fault by stopping a service on a host."""
        self.logger.info(f"Injected service down fault on {host_name} for service {service_name}.")
        self.kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation="stop")

    def recover_service_down(self, host_name: str, service_name: str):
        """Recover from a fault by starting a service on a host."""
        self.logger.info(f"Recovered service down fault on {host_name} for service {service_name}.")
        self.kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation="start")

    def inject_bmv2_down(self, host_name: str):
        """Inject a fault by stopping the bmv2 service on a host."""
        self.kathara_api.exec_cmd(host_name, "pkill simple_switch")
        self.logger.info(f"Injected bmv2 down fault on {host_name}.")

    def recover_bmv2_down(self, host_name: str):
        """Recover from a fault by starting the bmv2 service on a host.
        Note: make sure bmv2 is started via the host's startup script.
        """
        cmd = f"./hostlab/{host_name}.startup"
        self.kathara_api.exec_cmd(host_name, cmd)
        self.logger.info(f"Recovered bmv2 down fault on {host_name}.")

    def inject_bgp_misconfig(self, host_name: str, correct_asn: int, wrong_asn: int):
        """Inject a BGP ASN misconfiguration by changing the ASN on a router, from real_asn to target_asn."""
        self.kathara_api.exec_cmd(
            host_name,
            f"vtysh -c 'show running-config' | sed 's/^router bgp {correct_asn}$/router bgp {wrong_asn}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Injected BGP ASN misconfiguration on {host_name} from ASN {correct_asn} to {wrong_asn}.")

    def recover_bgp_misconfig(self, host_name: str, correct_asn: int, wrong_asn: int):
        """Recover from a BGP ASN misconfiguration by resetting the ASN on a router."""
        self.kathara_api.exec_cmd(
            host_name,
            f"vtysh -c 'show running-config' | sed 's/^router bgp {wrong_asn}$/router bgp {correct_asn}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Recovered BGP ASN misconfiguration on {host_name} from ASN {wrong_asn} to {correct_asn}.")

    def inject_bgp_remove_advertisement(self, host_name: str):
        """Inject a BGP missing route by commenting out the network advertisement."""
        self.kathara_api.exec_cmd(
            host_name,
            "sed -i.bak -E 's/^([[:space:]]*)network /\1# network /' /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Injected BGP missing route on {host_name}.")

    def recover_bgp_remove_advertisement(self, host_name: str):
        """Recover from a BGP missing route by recovering the backed up frr.conf file."""
        self.kathara_api.exec_cmd(
            host_name,
            "mv /etc/frr/frr.conf.bak /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Recovered BGP missing route on {host_name}.")

    def inject_default_route_missing(self, host_name: str, back_up_file: str = "/tmp/default_route_backup.txt"):
        """Inject a fault by removing the default route on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "ip route show default > " + back_up_file,
        )
        self.kathara_api.exec_cmd(
            host_name,
            "ip route del default",
        )
        self.logger.info(f"Injected removal of default route on {host_name}.")

    def recover_default_route_missing(self, host_name: str, back_up_file: str = "/tmp/default_route_backup.txt"):
        """Recover from a fault by adding the default route on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "sh -c 'cat " + back_up_file + " | xargs ip route add'",
        )
        self.logger.info(f"Recovered removal of default route on {host_name}.")

    def inject_add_route_blackhole_nexthop(self, host_name: str, network: str):
        """Inject a fault by adding a static blackhole route on a host."""
        res = self.kathara_api.exec_cmd(
            host_name,
            f"ip route add blackhole {network}",
        )
        print(res)
        self.logger.info(f"Injected addition of route {network} on {host_name}.")

    def recover_add_route_blackhole_nexthop(self, host_name: str, network: str):
        """Recover from a fault by deleting a static blackhole route on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"ip route del blackhole {network}",
        )
        self.logger.info(f"Recovered addition of route {network} on {host_name}.")

    def inject_add_route_blackhole_advertise(self, host_name: str, network: str, AS: str):
        cmd = (
            "vtysh -c 'configure terminal' "
            f"-c 'ip route {network} Null0' "
            f"-c 'router bgp {AS}' "
            f"-c 'network {network}' "
            "-c 'end' "
            "-c 'write memory' "
        )
        self.kathara_api.exec_cmd(
            host_name,
            cmd,
        )
        self.logger.info(f"Injected BGP advertise blackhole route on {host_name}: {network}.")

    def recover_add_route_blackhole_advertise(self, host_name: str, network: str, AS: str):
        cmd = (
            "vtysh -c 'configure terminal' "
            f"-c 'no ip route {network} Null0' "
            f"-c 'router bgp {AS}' "
            f"-c 'no network {network}' "
            "-c 'end' "
            "-c 'write memory' "
        )
        self.kathara_api.exec_cmd(
            host_name,
            cmd,
        )
        self.logger.info(f"Recovered BGP advertise blackhole route on {host_name}: {network}.")

    def inject_rip_missing_route(self, host_name: str, network: str):
        """Inject a RIP missing route by commenting out the network advertisement."""
        cmd = f"vtysh -c 'configure terminal' -c 'router rip' -c 'no network {network}' -c 'end' -c 'write memory' && systemctl restart frr"
        res = self.kathara_api.exec_cmd(
            host_name,
            cmd,
        )
        self.logger.info(f"Injected RIP missing route on {host_name}: {network}.")

    def recover_rip_missing_route(self, host_name: str, network: str):
        """Recover from a RIP missing route by recovering the backed up frr.conf file."""
        cmd = f"vtysh -c 'configure terminal' -c 'router rip' -c 'network {network}' -c 'end' -c 'write memory' && systemctl restart frr"
        self.kathara_api.exec_cmd(
            host_name,
            cmd,
        )
        self.logger.info(f"Recovered RIP missing route on {host_name}: {network}.")


if __name__ == "__main__":
    # Example usage
    injector = FaultInjectorBase("simple_bgp")
    # injector.inject_fragmentation_disabled("router1", mtu=100)
    injector.recover_fragmentation_disabled("router1")
