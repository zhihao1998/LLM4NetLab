from llm4netlab.generator.fault.injector_base import BaseFaultInjector
from llm4netlab.service.kathara import KatharaIntfAPI, KatharaTCAPI

""" Fault injector for Kathara """


class KatharaAPI_Intf_TC(KatharaIntfAPI, KatharaTCAPI):
    """Combined API for Kathara interface and traffic control operations."""

    pass


class KatharaBaseFaultInjector(BaseFaultInjector):
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAPI_Intf_TC(lab_name)

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


if __name__ == "__main__":
    # Example usage
    # injector = KatharaBaseFaultInjector("simple_bmv2")
    # injector.inject_packet_loss("s1", "eth0", 50)
    # print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    # injector.recover_packet_loss("s1", "eth0")
    # print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    injector = KatharaBaseFaultInjector("ospf_frr_single_area")
    device_name = "eth0"
    injector.inject_link_failure("bb0", device_name)
    print(injector.kathara_api.intf_show("bb0", device_name))
    injector.recover_link_failure("bb0", device_name)
    print(injector.kathara_api.intf_show("bb0", device_name))
