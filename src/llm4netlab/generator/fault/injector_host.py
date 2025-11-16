import logging

from llm4netlab.service.kathara import KatharaAPIALL


class FaultInjectorHost:
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAPIALL(lab_name)
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

    def inject_remove_ip(self, host_name: str, ip_address: str, intf_name: str):
        """Inject a fault by removing an IP address from a host interface."""
        self.kathara_api.exec_cmd(
            host_name,
            f"ip addr del {ip_address} dev {intf_name}",
        )
        self.logger.info(f"Injected removal of IP {ip_address} on {host_name}:{intf_name}.")

    def recover_remove_ip(self, host_name: str, ip_address: str, intf_name: str):
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

    def inject_high_cpu(self, host_name: str, duration: int = 300):
        """Inject a fault by causing high CPU usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"stress-ng --cpu 0 --timeout {duration} &",
        )
        self.logger.info(f"Injected high CPU usage on {host_name} for {duration} seconds.")

    def recover_high_cpu(self, host_name: str):
        """Recover from high CPU usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "pkill stress-ng",
        )
        self.logger.info(f"Recovered high CPU usage on {host_name}.")

    def inject_high_memory(self, host_name: str, duration: int = 300):
        """Inject a fault by causing high memory usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"stress-ng --vm 0 --vm-bytes 75% -t {duration} &",
        )
        self.logger.info(f"Injected high memory usage on {host_name} for {duration} seconds.")

    def recover_high_memory(self, host_name: str):
        """Recover from high memory usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "pkill stress-ng",
        )
        self.logger.info(f"Recovered high memory usage on {host_name}.")

    def inject_high_socket(self, host_name: str, duration: int = 300):
        """Inject a fault by causing high socket usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"stress-ng --socket 10 --timeout {duration} &",
        )
        self.logger.info(f"Injected high socket usage on {host_name} for {duration} seconds.")

    def recover_high_socket(self, host_name: str):
        """Recover from high socket usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "pkill stress-ng",
        )
        self.logger.info(f"Recovered high socket usage on {host_name}.")

    def inject_high_io(self, host_name: str, duration: int = 300):
        """Inject a fault by causing high I/O usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"stress-ng --iomix 0 --timeout {duration} &",
        )
        self.logger.info(f"Injected high I/O usage on {host_name} for {duration} seconds.")

    def recover_high_io(self, host_name: str):
        """Recover from high I/O usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "pkill stress-ng",
        )
        self.logger.info(f"Recovered high I/O usage on {host_name}.")


if __name__ == "__main__":
    # Example usage
    injector = FaultInjectorHost("simple_bmv2")
    # injector.inject_bmv2_down("s1")
    # injector.recover_bmv2_down("s1")

    # injector.inject_packet_loss("s1", "eth0", 50)
    # print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    # injector.recover_packet_loss("s1", "eth0")
    # print(injector.kathara_api.tc_show_intf("s1", "eth0"))
    # injector = FaultInjectorBase("ospf_frr_single_area")
    # device_name = "eth0"
    # injector.inject_link_failure("bb0", device_name)
    # print(injector.kathara_api.intf_show("bb0", device_name))
    # injector.recover_link_failure("bb0", device_name)
    # print(injector.kathara_api.intf_show("bb0", device_name))
    # injector = FaultInjectorBase("simple_bgp")
    # rule = "tcp dport 179 drop"
    # injector.inject_acl_rule("router1", rule)
    # rule = "tcp sport 179 drop"
    # injector.inject_acl_rule("router1", rule)
    # injector.recover_acl_rule("router1")
    # injector.inject_service_down("router1", "frr")
