from llm4netlab.generator.fault.injector_base import BaseFaultInjector
from llm4netlab.service.kathara_api import KatharaAPI

""" Fault injector for Kathara P4 environments, specifically for Bmv2 switches."""


class KatharaBaseFaultInjector(BaseFaultInjector):
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAPI(lab_name)

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


if __name__ == "__main__":
    # Example usage
    injector = KatharaBaseFaultInjector("simple_bmv2")
    injector.inject_packet_loss("s1", "eth0", 50)
    print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    injector.recover_packet_loss("s1", "eth0")
    print(injector.kathara_api.tc_show_intf("s1", "eth0"))
