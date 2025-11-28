
from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger

""" Fault injector for Linux Traffic Control (tc) related faults """


class FaultInjectorTC:
    def __init__(self, lab_name: str):
        self.kathara_api = KatharaAPIALL(lab_name)
        self.logger = system_logger

    def inject_packet_loss(self, host_name: str, intf_name: str, loss_percentage: int):
        """Inject packet loss into a specific intf_name of a switch."""
        self.kathara_api.tc_set_netem(
            host_name=host_name,
            intf_name=intf_name,
            loss=loss_percentage,
        )
        self.logger.info(f"Injected packet loss of {loss_percentage}% on {host_name}:{intf_name}")

    def recover_packet_loss(self, host_name: str, intf_name: str):
        """Recover from packet loss by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            intf_name=intf_name,
        )
        self.logger.info(f"Recovered packet loss (via clearing TC rules) on {host_name}:{intf_name}")

    def inject_delay(self, host_name: str, intf_name: str, delay_ms: int, limit: int = None):
        """Inject a delay into a specific intf_name of a switch."""
        self.kathara_api.tc_set_netem(
            host_name=host_name,
            intf_name=intf_name,
            delay_ms=delay_ms,
            limit=limit,
        )
        self.logger.info(f"Injected delay of {delay_ms}ms on {host_name}:{intf_name}")

    def recover_delay(self, host_name: str, intf_name: str):
        """Recover from a delay injection by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            intf_name=intf_name,
        )
        self.logger.info(f"Recovered delay (via clearing TC rules) on {host_name}:{intf_name}")

    def inject_jitter(self, host_name: str, intf_name: str, delay_ms: int = 2, jitter_ms: int = 1000):
        """Inject jitter into a specific intf_name of a switch."""
        self.kathara_api.tc_set_netem(
            host_name=host_name,
            intf_name=intf_name,
            delay_ms=delay_ms,
            jitter_ms=jitter_ms,
        )
        self.logger.info(f"Injected jitter of {jitter_ms}ms on {host_name}:{intf_name}")

    def recover_jitter(self, host_name: str, intf_name: str):
        """Recover from jitter by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            intf_name=intf_name,
        )
        self.logger.info(f"Recovered jitter (via clearing TC rules) on {host_name}:{intf_name}")

    def inject_packet_corruption(self, host_name: str, intf_name: str, corruption_percentage: int):
        """Inject packet corruption into a specific intf_name of a switch."""
        self.kathara_api.tc_set_netem(
            host_name=host_name,
            intf_name=intf_name,
            corrupt=corruption_percentage,
        )
        self.logger.info(f"Injected packet corruption of {corruption_percentage}% on {host_name}:{intf_name}")

    def recover_packet_corruption(self, host_name: str, intf_name: str):
        """Recover from packet corruption by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            intf_name=intf_name,
        )
        self.logger.info(f"Recovered packet corruption (via clearing TC rules) on {host_name}:{intf_name}")

    def inject_bandwidth_limit(self, host_name: str, intf_name: str, rate: str, burst: str, limit: str):
        """Inject bandwidth limit into a specific intf_name of a switch."""
        self.kathara_api.tc_set_tbf(
            host_name=host_name,
            intf_name=intf_name,
            rate=rate,
            burst=burst,
            limit=limit,
        )
        self.logger.info(
            f"Injected bandwidth limit of {rate}mbit with burst {burst} and limit {limit} on {host_name}:{intf_name}"
        )

    def recover_bandwidth_limit(self, host_name: str, intf_name: str):
        """Recover from bandwidth limit by removing traffic control settings."""
        self.kathara_api.tc_clear_intf(
            host_name=host_name,
            intf_name=intf_name,
        )
        self.logger.info(f"Recovered bandwidth limit (via clearing TC rules) on {host_name}:{intf_name}")


if __name__ == "__main__":
    # Example usage
    injector = FaultInjectorTC("dc_clos_service")
    injector.inject_delay("dns_pod0", "eth0", 1000)
    # print(injector.kathara_api.tc_show_intf("leaf_0_1", "eth0"))
    # injector.recover_bandwidth_limit("dns_pod0", "eth0")
