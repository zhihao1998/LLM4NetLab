import logging

from llm4netlab.service.kathara import KatharaAPIALL

""" Fault injector for Linux Traffic Control (tc) related faults """


class FaultInjectorTC:
    def __init__(self, lab_name: str):
        self.kathara_api = KatharaAPIALL(lab_name)
        self.logger = logging.getLogger(__name__)

    def inject_packet_loss(self, host_name: str, interface: str, loss_percentage: int):
        """Inject packet loss into a specific interface of a switch."""
        self.kathara_api.tc_set_netem(
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
        self.kathara_api.tc_set_netem(
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

    def inject_packet_corruption(self, host_name: str, interface: str, corruption_percentage: int):
        """Inject packet corruption into a specific interface of a switch."""
        self.kathara_api.tc_set_netem(
            host_name=host_name,
            interface=interface,
            corrupt=corruption_percentage,
        )
        self.logger.info(f"Injected packet corruption of {corruption_percentage}% on {host_name}:{interface}")

    def recover_packet_corruption(self, host_name: str, interface: str):
        """Recover from packet corruption by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            interface=interface,
        )
        self.logger.info(f"Recovered packet corruption (via clearing TC rules) on {host_name}:{interface}")

    def inject_bandwidth_limit(self, host_name: str, interface: str, rate: str, burst: str):
        """Inject bandwidth limit into a specific interface of a switch."""
        self.kathara_api.tc_set_tbf(
            host_name=host_name,
            interface=interface,
            rate=rate,
            burst=burst,
        )
        self.logger.info(f"Injected bandwidth limit of {rate}mbit with burst {burst} on {host_name}:{interface}")

    def recover_bandwidth_limit(self, host_name: str, interface: str):
        """Recover from bandwidth limit by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            interface=interface,
        )
        self.logger.info(f"Recovered bandwidth limit (via clearing TC rules) on {host_name}:{interface}")


if __name__ == "__main__":
    # Example usage
    injector = FaultInjectorTC("dc_clos_service")
    injector.inject_delay("dns_pod0", "eth0", 1000)
    # print(injector.kathara_api.tc_show_intf("leaf_0_1", "eth0"))
    # injector.recover_bandwidth_limit("dns_pod0", "eth0")
