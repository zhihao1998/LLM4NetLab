import logging

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Host missing IP address """


class HostMissingIPBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_missing_ip"

    symptom_desc = "Some hosts are unable to communicate with other devices in the network."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[0]
        self.intf_name = "eth0"

    def inject_fault(self):
        real_ip = self.kathara_api.get_host_ip(self.faulty_devices, self.intf_name, with_prefix=True)
        real_gateway = self.kathara_api.get_default_gateway(self.faulty_devices)
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices,
            command=f"ip addr del {real_ip} dev {self.intf_name}",
        )
        # backup the removed IP to a file for recovery
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices,
            command=f"echo '{real_ip} {real_gateway}' > /tmp/removed_ip.txt",
        )
        self.logger.info(f"Injected missing IP on {self.faulty_devices} from {real_ip} and gateway {real_gateway}.")

    def recover_fault(self):
        # read the backed-up IP from the file
        output = self.kathara_api.exec_cmd(
            host_name=self.faulty_devices,
            command="cat /tmp/removed_ip.txt",
        )
        real_ip, real_gateway = output.strip().split()
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices,
            command=f"ip addr add {real_ip} dev {self.intf_name}",
        )
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices,
            command="ip route add default via " + real_gateway,
        )
        # remove the backup file
        self.kathara_api.exec_cmd(
            host_name=self.faulty_devices,
            command="rm /tmp/removed_ip.txt",
        )
        self.logger.info(f"Recovered missing IP on {self.faulty_devices} to {real_ip} and gateway {real_gateway}.")


class HostMissingIPDetection(HostMissingIPBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostMissingIPBase.root_cause_category,
        root_cause_name=HostMissingIPBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostMissingIPLocalization(HostMissingIPBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostMissingIPBase.root_cause_category,
        root_cause_name=HostMissingIPBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostMissingIPRCA(HostMissingIPBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostMissingIPBase.root_cause_category,
        root_cause_name=HostMissingIPBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
""" Problem: Host IP conflict """


class HostIPConflictBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_ip_conflict"

    symptom_desc = "Some hosts experience intermittent connectivity issues."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[:2]

    def inject_fault(self):
        self.injector.inject_ip_change(
            host_name=self.faulty_device[1],
            old_ip=self.kathara_api.get_host_ip(self.faulty_device[1], "eth0", with_prefix=True),
            new_ip=self.kathara_api.get_host_ip(self.faulty_device[0], "eth0", with_prefix=True),
            intf_name="eth0",
            new_gateway=self.kathara_api.get_default_gateway(self.faulty_device[0]),
        )

    def recover_fault(self):
        ip_address = f"10.1.1.{200}"  # Assign a new IP to avoid conflict
        self.injector.recover_ip_change(
            host_name=self.faulty_device[1],
            old_ip=self.kathara_api.get_host_ip(self.faulty_device[1], "eth0", with_prefix=True),
            new_ip=ip_address,
            intf_name="eth0",
            old_gateway=self.kathara_api.get_default_gateway(self.faulty_device[1]),
        )


class HostIPConflictDetection(HostIPConflictBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIPConflictBase.root_cause_category,
        root_cause_name=HostIPConflictBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostIPConflictLocalization(HostIPConflictBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIPConflictBase.root_cause_category,
        root_cause_name=HostIPConflictBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostIPConflictRCA(HostIPConflictBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIPConflictBase.root_cause_category,
        root_cause_name=HostIPConflictBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
""" Problem: Incorrect Host IP """


class HostIncorrectIPBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_incorrect_ip"

    symptom_desc = "Some hosts seem to be unreachable in the network."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[0]

    def inject_fault(self):
        incorrect_ip = "10.2.1.20/24"
        ip_gateway = "10.2.1.1"
        self.injector.inject_ip_change(
            host_name=self.faulty_devices,
            old_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            new_ip=incorrect_ip,
            intf_name="eth0",
            new_gateway=ip_gateway,
        )

    def recover_fault(self):
        self.injector.recover_ip_change(
            host_name=self.faulty_devices,
            old_ip=self.incorrect_ip,
            new_ip="10.1.1.2/24",
            intf_name="eth0",
            old_gateway="10.1.1.1",
        )


class HostIncorrectIPDetection(HostIncorrectIPBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectIPBase.root_cause_category,
        root_cause_name=HostIncorrectIPBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostIncorrectIPLocalization(HostIncorrectIPBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectIPBase.root_cause_category,
        root_cause_name=HostIncorrectIPBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostIncorrectIPRCA(HostIncorrectIPBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectIPBase.root_cause_category,
        root_cause_name=HostIncorrectIPBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
""" Problem: Incorrect Host Gateway """


class HostIncorrectGatewayBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_incorrect_gateway"

    symptom_desc = "Some hosts seem to be unreachable in the network."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[0]

    def inject_fault(self):
        try:
            new_gateway_list = self.kathara_api.get_default_gateway(self.faulty_device).split(".")
            new_gateway_list[-1] = "254"
            new_gateway = ".".join(new_gateway_list)
        except Exception:
            new_gateway = "10.0.0.254"
        self.injector.inject_ip_change(
            host_name=self.faulty_devices,
            old_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            new_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            intf_name="eth0",
            new_gateway=new_gateway,
        )

    def recover_fault(self):
        try:
            old_gateway_list = self.kathara_api.get_default_gateway(self.faulty_device).split(".")
            old_gateway_list[-1] = "1"
            old_gateway = ".".join(old_gateway_list)
        except Exception:
            old_gateway = "10.1.1.1"
        self.injector.recover_ip_change(
            host_name=self.faulty_devices,
            old_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            new_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            intf_name="eth0",
            old_gateway=old_gateway,
        )


class HostIncorrectGatewayDetection(HostIncorrectGatewayBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectGatewayBase.root_cause_category,
        root_cause_name=HostIncorrectGatewayBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostIncorrectGatewayLocalization(HostIncorrectGatewayBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectGatewayBase.root_cause_category,
        root_cause_name=HostIncorrectGatewayBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


# ==========================================
""" Problem: Incorrect Host netmask """


class HostIncorrectNetmaskBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_incorrect_netmask"

    symptom_desc = "Some hosts seem to be unreachable in the network."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[0]

    def inject_fault(self):
        new_ip = self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True)
        new_ip = new_ip.split("/")
        new_ip[-1] = "8"
        new_ip = "/".join(new_ip)

        self.injector.inject_ip_change(
            host_name=self.faulty_devices,
            old_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            new_ip=new_ip,
            intf_name="eth0",
            new_gateway=self.kathara_api.get_default_gateway(self.faulty_device),
        )

    def recover_fault(self):
        old_ip = self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True)
        old_ip = old_ip.split("/")
        old_ip[-1] = "24"
        old_ip = "/".join(old_ip)

        self.injector.recover_ip_change(
            host_name=self.faulty_devices,
            old_ip=self.kathara_api.get_host_ip(self.faulty_devices, "eth0", with_prefix=True),
            new_ip=old_ip,
            intf_name="eth0",
            old_gateway=self.kathara_api.get_default_gateway(self.faulty_device),
        )


class HostIncorrectNetmaskDetection(HostIncorrectNetmaskBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectNetmaskBase.root_cause_category,
        root_cause_name=HostIncorrectNetmaskBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostIncorrectNetmaskLocalization(HostIncorrectNetmaskBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectNetmaskBase.root_cause_category,
        root_cause_name=HostIncorrectNetmaskBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostIncorrectNetmaskRCA(HostIncorrectNetmaskBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectNetmaskBase.root_cause_category,
        root_cause_name=HostIncorrectNetmaskBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
# Problem: Incorrect Host DNS resolvers
# =========================================


class HostIncorrectDNSBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_incorrect_dns"

    symptom_desc = "Some hosts are unable to access web services."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[0]

    def inject_fault(self):
        self.injector.inject_dns_misconfiguration(
            host_name=self.faulty_devices,
        )

    def recover_fault(self):
        self.injector.recover_dns_misconfiguration(
            host_name=self.faulty_devices,
            original_dns_ip=self.net_env.dns_ip,
        )


class HostIncorrectDNSDetection(HostIncorrectDNSBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectDNSBase.root_cause_category,
        root_cause_name=HostIncorrectDNSBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostIncorrectDNSLocalization(HostIncorrectDNSBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectDNSBase.root_cause_category,
        root_cause_name=HostIncorrectDNSBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostIncorrectDNSRCA(HostIncorrectDNSBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectDNSBase.root_cause_category,
        root_cause_name=HostIncorrectDNSBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==========================================
# Problem: Host MAC address spoofing
# =========================================


class HostMACSpoofingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_mac_spoofing"

    symptom_desc = "Some hosts experience intermittent connectivity issues."

    def __init__(self, net_env_name: str | None, **kwargs):
        self.net_env = get_net_env_instance(net_env_name, **kwargs) or OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.hosts[:2]

        self.spoofed_mac = "00:11:22:33:44:55"

    def inject_fault(self):
        self.kathara_api.exec_cmd(
            host_name=self.faulty_device[0],
            command=f"ifconfig eth0 hw ether {self.spoofed_mac}",
        )
        self.kathara_api.exec_cmd(
            host_name=self.faulty_device[1],
            command=f"ifconfig eth0 hw ether {self.spoofed_mac}",
        )

    def recover_fault(self):
        new_mac_1 = self.spoofed_mac.replace("55", "66")
        new_mac_2 = self.spoofed_mac.replace("55", "77")
        self.kathara_api.exec_cmd(
            host_name=self.faulty_device[0],
            command=f"ifconfig eth0 hw ether {new_mac_1}",
        )
        self.kathara_api.exec_cmd(
            host_name=self.faulty_device[1],
            command=f"ifconfig eth0 hw ether {new_mac_2}",
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    host_ip_conflict = HostMACSpoofingBase()
    host_ip_conflict.recover_fault()
