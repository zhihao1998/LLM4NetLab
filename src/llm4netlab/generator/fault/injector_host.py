from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger


class FaultInjectorHost:
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAPIALL(lab_name)
        self.logger = system_logger

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
        self.logger.info(
            f"Injected IP change from {old_ip} to {new_ip} on {host_name}:{intf_name}, default gateway changed to {new_gateway}."
        )

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
            f"stress-ng --cpu 0  --cpu-load 100 --timeout {duration} &",
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
            f"stress-ng --sock 0 --timeout {duration} &",
        )
        self.logger.info(f"Injected high socket usage on {host_name} for {duration} seconds.")

    def recover_high_socket(self, host_name: str):
        """Recover from high socket usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "pkill stress-ng",
        )
        self.logger.info(f"Recovered high socket usage on {host_name}.")

    def inject_stress_all(self, host_name: str, duration: int = 300):
        """Inject a fault by causing high CPU, memory, and I/O usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"stress-ng --cpu 0 --cpu-load 100 --iomix 0 --sock 0 --hdd 2 -vm 0 --vm-bytes 75% --timeout {duration} &",
        )
        self.logger.info(f"Injected high CPU, memory, and I/O usage on {host_name} for {duration} seconds.")

    def recover_stress_all(self, host_name: str):
        """Recover from high CPU, memory, and I/O usage on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            "pkill stress-ng",
        )
        self.logger.info(f"Recovered high CPU, memory, and I/O usage on {host_name}.")

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

    def inject_dns_misconfiguration(self, host_name: str, fake_dns_ip: str = "8.8.8.8"):
        """Inject a fault by misconfiguring DNS on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"echo 'nameserver {fake_dns_ip}' > /etc/resolv.conf",
        )
        self.logger.info(f"Injected DNS misconfiguration on {host_name} with fake DNS {fake_dns_ip}.")

    def recover_dns_misconfiguration(self, host_name: str, original_dns_ip: str):
        """Recover from DNS misconfiguration on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"echo 'nameserver {original_dns_ip}' > /etc/resolv.conf",
        )
        self.logger.info(f"Recovered DNS misconfiguration on {host_name} with original DNS {original_dns_ip}.")

    def inject_arp_misconfiguration(self, host_name: str, ip_address: str, fake_mac: str = "00:11:22:33:44:55"):
        """Inject a fault by misconfiguring ARP on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"arp -s {ip_address} {fake_mac}",
        )
        self.logger.info(f"Injected ARP misconfiguration on {host_name} for IP {ip_address} with fake MAC {fake_mac}.")

    def recover_arp_misconfiguration(self, host_name: str, ip_address: str):
        """Recover from ARP misconfiguration on a host."""
        self.kathara_api.exec_cmd(
            host_name,
            f"arp -d {ip_address}",
        )
        self.logger.info(f"Recovered ARP misconfiguration on {host_name}.")


if __name__ == "__main__":
    # Example usage
    injector = FaultInjectorHost("dc_clos_service")
    injector.recover_dns_misconfiguration("client_0", original_dns_ip="10.0.0.2")
