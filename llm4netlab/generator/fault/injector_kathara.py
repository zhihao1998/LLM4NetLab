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

    def recover_delay(self, host_name: str, interface: str):
        """Recover from a delay injection by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            interface=interface,
        )
        self.logger.info(f"Recovered delay (via clearing TC rules) on {host_name}:{interface}")

    def inject_link_failure(self, host_name: str, interface: str):
        """Inject a link failure by disabling the interface."""
        self.kathara_api.intf_down(host_name=host_name, interface=interface)
        self.logger.info(f"Injected link failure on {host_name}:{interface}")

    def recover_link_failure(self, host_name: str, interface: str):
        """Recover from a link failure by enabling the interface."""
        self.kathara_api.intf_up(host_name=host_name, interface=interface)
        self.logger.info(f"Recovered link failure on {host_name}:{interface}")

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
        self.kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation="stop")
        self.logger.info(f"Injected service down fault on {host_name} for service {service_name}.")

    def recover_service_down(self, host_name: str, service_name: str):
        """Recover from a fault by starting a service on a host."""
        self.kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation="start")
        self.logger.info(f"Recovered service down fault on {host_name} for service {service_name}.")

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


if __name__ == "__main__":
    # Example usage
    injector = KatharaBaseFaultInjector("simple_bmv2")
    # injector.inject_bmv2_down("s1")
    # injector.recover_bmv2_down("s1")

    # injector.inject_packet_loss("s1", "eth0", 50)
    # print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    # injector.recover_packet_loss("s1", "eth0")
    # print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    # injector = KatharaBaseFaultInjector("ospf_frr_single_area")
    # device_name = "eth0"
    # injector.inject_link_failure("bb0", device_name)
    # print(injector.kathara_api.intf_show("bb0", device_name))
    # injector.recover_link_failure("bb0", device_name)
    # print(injector.kathara_api.intf_show("bb0", device_name))
    # injector = KatharaBaseFaultInjector("simple_bgp")
    # rule = "tcp dport 179 drop"
    # injector.inject_acl_rule("router1", rule)
    # rule = "tcp sport 179 drop"
    # injector.inject_acl_rule("router1", rule)
    # injector.recover_acl_rule("router1")
    # injector.inject_service_down("router1", "frr")
