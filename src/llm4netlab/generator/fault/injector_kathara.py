import logging

from llm4netlab.generator.fault.injector_base import BaseFaultInjector
from llm4netlab.service.kathara import KatharaFRRAPI, KatharaIntfAPI, KatharaNFTableAPI, KatharaTCAPI

""" Fault injector for Kathara """


class KatharaAllInOneAPI(KatharaIntfAPI, KatharaTCAPI, KatharaNFTableAPI, KatharaFRRAPI):
    pass


class KatharaBaseFaultInjector(BaseFaultInjector):
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAllInOneAPI(lab_name)
        self.logger = logging.getLogger(__name__)

    def inject_packet_loss(self, host_name: str, interface: str, loss_percentage: int):
        """Inject packet loss into a specific interface of a switch."""
        self.kathara_api.tc_set_intf(
            host_name=host_name,
            interface=interface,
            loss=loss_percentage,
        )
        self.logger.info(f"Injected packet loss of {loss_percentage}% on {host_name}:{interface}")

    def recover_packet_loss(self, host_name: str, interface: str):
        """Recover from packet loss by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            interface=interface,
        )
        self.logger.info(f"Recovered packet loss (via clearing TC rules) on {host_name}:{interface}")

    def inject_delay(self, host_name: str, interface: str, delay: int):
        """Inject a delay into a specific interface of a switch."""
        self.kathara_api.tc_set_intf(
            host_name=host_name,
            interface=interface,
            delay=delay,
        )
        self.logger.info(f"Injected delay of {delay}ms on {host_name}:{interface}")

    def recover_delay(self, host_name: str, intf_name: str):
        """Recover from a delay injection by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            interface=intf_name,
        )
        self.logger.info(f"Recovered delay (via clearing TC rules) on {host_name}:{intf_name}")

    def inject_intf_down(self, host_name: str, intf_name: str):
        """Bring down a specific interface of a host."""
        self.kathara_api.intf_on_off(host_name=host_name, interface=intf_name, state="down")
        self.logger.info(f"Injected interface down on {host_name}:{intf_name}")

    def recover_intf_down(self, host_name: str, intf_name: str):
        """Recover from an interface down by enabling the interface."""
        self.kathara_api.intf_on_off(host_name=host_name, interface=intf_name, state="up")
        self.logger.info(f"Recovered interface down on {host_name}:{intf_name}")

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

    def inject_ospf_area_misconfig(self, host_name: str, correct_area: int, wrong_area: int):
        """Inject a OSPF area misconfiguration by changing the area on a router, from real_area to target_area."""
        self.kathara_api.exec_cmd(
            host_name,
            f"vtysh -c 'show running-config' | sed -E 's/(area )({correct_area})$/\\1{wrong_area}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(
            f"Injected OSPF area misconfiguration on {host_name} from area {correct_area} to {wrong_area}."
        )

    def recover_ospf_area_misconfig(self, host_name: str, correct_area: int, wrong_area: int):
        """Recover from a OSPF area misconfiguration by resetting the area on a router."""
        self.kathara_api.exec_cmd(
            host_name,
            f"vtysh -c 'show running-config' | sed -E 's/(area )({wrong_area})$/\\1{correct_area}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(
            f"Recovered OSPF area misconfiguration on {host_name} from area {wrong_area} to {correct_area}."
        )

    def inject_bgp_missing_route(self, host_name: str):
        """Inject a BGP missing route by commenting out the network advertisement."""
        self.kathara_api.exec_cmd(
            host_name,
            "sed -i.bak -E 's/^([[:space:]]*)network /\1# network /' /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Injected BGP missing route on {host_name}.")

    def recover_bgp_missing_route(self, host_name: str):
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
        self.kathara_api.exec_cmd(
            host_name,
            f"ip route add blackhole {network}",
        )
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
    injector = KatharaBaseFaultInjector("rip_small_internet")
