import logging

from llm4netlab.generator.fault.injector_base import BaseFaultInjector
from llm4netlab.service.kathara import KatharaIntfAPI, KatharaNFTableAPI, KatharaTCAPI

""" Fault injector for Kathara """


class KatharaAllInOneAPI(KatharaIntfAPI, KatharaTCAPI, KatharaNFTableAPI):
    pass


class KatharaBaseFaultInjector(BaseFaultInjector):
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAllInOneAPI(lab_name)
        self.logger = logging.getLogger("fault_injector.kathara.base")

    def inject_packet_loss(self, host_name: str, interface: str, loss_percentage: int):
        """Inject packet loss into a specific interface of a switch."""
        self.kathara_api.tc_set_intf(
            host_name=host_name,
            interface=interface,
            loss=loss_percentage,
        )

    def recover_packet_loss(self, host_name: str, interface: str):
        """Recover from packet loss by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            interface=interface,
        )

    def inject_link_failure(self, host_name: str, interface: str):
        """Inject a link failure by disabling the interface."""
        self.kathara_api.intf_down(host_name=host_name, interface=interface)

    def recover_link_failure(self, host_name: str, interface: str):
        """Recover from a link failure by enabling the interface."""
        self.kathara_api.intf_up(host_name=host_name, interface=interface)

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

    def recover_acl_rule(self, host_name: str, table_name: str = "filter"):
        """Recover from an ACL rule by deleting the filter table."""
        self.kathara_api.nft_delete_table(host_name=host_name, table_name=table_name)

    def inject_service_down(self, host_name: str, service_name: str):
        """Inject a fault by stopping a service on a host."""
        self.kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation="stop")
        self.logger.info(f"Injected service down fault on {host_name} for service {service_name}.")

    def recover_service_down(self, host_name: str, service_name: str):
        """Recover from a fault by starting a service on a host."""
        self.kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation="start")
        self.logger.info(f"Recovered service down fault on {host_name} for service {service_name}.")


if __name__ == "__main__":
    # Example usage
    # injector = KatharaBaseFaultInjector("simple_bmv2")
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
    injector = KatharaBaseFaultInjector("simple_bgp")
    # rule = "tcp dport 179 drop"
    # injector.inject_acl_rule("router1", rule)
    # rule = "tcp sport 179 drop"
    # injector.inject_acl_rule("router1", rule)
    # injector.recover_acl_rule("router1")
    injector.inject_service_down("router1", "frr")
