import logging

from llm4netlab.generator.fault.injector_base import BaseFaultInjector
from llm4netlab.service.kathara import KatharaFRRAPI, KatharaIntfAPI, KatharaNFTableAPI, KatharaTCAPI

""" Fault injector for Kathara """


class KatharaAllInOneAPI(KatharaIntfAPI, KatharaTCAPI, KatharaNFTableAPI, KatharaFRRAPI):
    pass


class KatharaHostFaultInjector(BaseFaultInjector):
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAllInOneAPI(lab_name)
        self.logger = logging.getLogger(__name__)

    def inject_host_default_route_missing(self, host_name: str, back_up_file: str = "/tmp/default_route_backup.txt"):
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

    def recover_host_default_route_missing(self, host_name: str, back_up_file: str = "/tmp/default_route_backup.txt"):
        """Recover from a fault by adding the default route on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "sh -c 'cat " + back_up_file + " | xargs ip route add'",
        )
        self.logger.info(f"Recovered removal of default route on {host_name}.")

    def inject_ip_missing(self, host_name: str, ip_address: str, intf_name: str):
        """Inject a fault by removing an IP address from a host interface."""
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr del {ip_address} dev {intf_name}",
        )
        self.logger.info(f"Injected removal of IP {ip_address} on {host_name}:{intf_name}.")

    def recover_ip_missing(self, host_name: str, ip_address: str, intf_name: str):
        """Recover from a fault by adding an IP address to a host interface."""
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr add {ip_address} dev {intf_name}",
        )
        self.logger.info(f"Recovered removal of IP {ip_address} on {host_name}:{intf_name}.")

    def inject_ip_change(self, host_name: str, old_ip: str, new_ip: str, intf_name: str, new_gateway: str = None):
        """Inject a fault by changing an IP address on a host interface."""
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr del {old_ip} dev {intf_name}",
        )
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr add {new_ip} dev {intf_name}",
        )
        # add default route if old_ip was default route
        self.kathara_api.exec_cmd(
            host_name,
            f"ip route add default via {new_gateway}",
        )
        self.logger.info(f"Injected IP change from {old_ip} to {new_ip} on {host_name}:{intf_name}.")

    def recover_ip_change(self, host_name: str, old_ip: str, new_ip: str, intf_name: str, old_gateway: str = None):
        """Recover from a fault by reverting an IP address change on a host interface."""
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr del {new_ip} dev {intf_name}",
        )
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr add {old_ip} dev {intf_name}",
        )
        # restore default route if old_ip was default route
        self.kathara_api.exec_cmd(
            host_name,
            f"ip route add default via {old_gateway}",
        )
        self.logger.info(f"Recovered IP change from {new_ip} to {old_ip} on {host_name}:{intf_name}.")


if __name__ == "__main__":
    # Example usage
    injector = KatharaHostFaultInjector("simple_bmv2")
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
