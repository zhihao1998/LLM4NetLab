import logging

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Host missing IP address """


class HostMissingIPBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_missing_ip"

    faulty_device = "host_1_1_1_1"
    symptom_desc = "Some hosts are unable to communicate with other devices in the network."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_remove_ip(
            host_name=self.faulty_device,
            ip_address=self.kathara_api.get_host_ip(self.faulty_device, "eth0"),
            interface_name="eth0",
        )

    def recover_fault(self):
        self.injector.recover_remove_ip(
            host_name=self.faulty_device,
            ip_address="10.1.1.2",
            interface_name="eth0",
        )


class HostMissingIPDetection(HostMissingIPBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostMissingIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostMissingIPBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostMissingIPLocalization(HostMissingIPBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostMissingIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostMissingIPBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostMissingIPBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class HostMissingIPRCA(HostMissingIPBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostMissingIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostMissingIPBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=HostMissingIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostMissingIPBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
""" Problem: Host IP conflict """


class HostIPConflictBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_ip_conflict"

    faulty_device_1 = "host_1_1_1_1"
    faulty_device_2 = "host_1_1_1_2"
    symptom_desc = "Some hosts experience intermittent connectivity issues."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_ip_change(
            host_name=self.faulty_device_2,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device_2, "eth0", with_prefix=True),
            new_ip=self.kathara_api.get_host_ip(self.faulty_device_1, "eth0", with_prefix=True),
            intf_name="eth0",
            new_gateway=self.kathara_api.get_default_gateway(self.faulty_device_1),
        )

    def recover_fault(self):
        ip_address = f"10.1.1.{200}"  # Assign a new IP to avoid conflict
        self.injector.recover_ip_change(
            host_name=self.faulty_device_2,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device_2, "eth0", with_prefix=True),
            new_ip=ip_address,
            intf_name="eth0",
            old_gateway=self.kathara_api.get_default_gateway(self.faulty_device_2),
        )


class HostIPConflictDetection(HostIPConflictBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIPConflictBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIPConflictBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostIPConflictLocalization(HostIPConflictBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIPConflictBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIPConflictBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostIPConflictBase.faulty_device_1, HostIPConflictBase.faulty_device_2],
    )

    def __init__(self):
        super().__init__()


class HostIPConflictRCA(HostIPConflictBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIPConflictBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIPConflictBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=HostIPConflictBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIPConflictBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
""" Problem: Incorrect Host IP """


class HostIncorrectIPBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_incorrect_ip"

    faulty_device = "host_1_1_1_1"
    incorrect_ip = "10.2.1.20/24"
    ip_gateway = "10.2.1.1"
    symptom_desc = "Some hosts seem to be unreachable in the network."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_ip_change(
            host_name=self.faulty_device,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
            new_ip=self.incorrect_ip,
            intf_name="eth0",
            new_gateway=self.ip_gateway,
        )

    def recover_fault(self):
        self.injector.recover_ip_change(
            host_name=self.faulty_device,
            old_ip=self.incorrect_ip,
            new_ip="10.1.1.2/24",
            intf_name="eth0",
            old_gateway="10.1.1.1",
        )


class HostIncorrectIPDetection(HostIncorrectIPBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectIPBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostIncorrectIPLocalization(HostIncorrectIPBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectIPBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostIncorrectIPBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class HostIncorrectIPRCA(HostIncorrectIPBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectIPBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=HostIncorrectIPBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectIPBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
""" Problem: Incorrect Host Gateway """


class HostIncorrectGatewayBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_incorrect_gateway"

    faulty_device = "host_1_1_1_1"
    symptom_desc = "Some hosts seem to be unreachable in the network."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        try:
            new_gateway_list = self.kathara_api.get_default_gateway(self.faulty_device).split(".")
            new_gateway_list[-1] = "254"
            new_gateway = ".".join(new_gateway_list)
        except Exception:
            new_gateway = "10.0.0.254"
        self.injector.inject_ip_change(
            host_name=self.faulty_device,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
            new_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
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
            host_name=self.faulty_device,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
            new_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
            intf_name="eth0",
            old_gateway=old_gateway,
        )


class HostIncorrectGatewayDetection(HostIncorrectGatewayBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectGatewayBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectGatewayBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostIncorrectGatewayLocalization(HostIncorrectGatewayBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectGatewayBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectGatewayBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostIncorrectGatewayBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


# ==========================================
""" Problem: Incorrect Host netmask """


class HostIncorrectNetmaskBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_incorrect_netmask"

    faulty_device = "host_1_1_1_1"
    symptom_desc = "Some hosts seem to be unreachable in the network."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        new_ip = self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True)
        new_ip = new_ip.split("/")
        new_ip[-1] = "8"
        new_ip = "/".join(new_ip)

        self.injector.inject_ip_change(
            host_name=self.faulty_device,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
            new_ip=new_ip,
            intf_name="eth0",
            new_gateway=self.kathara_api.get_default_gateway(self.faulty_device),
        )

    def recover_fault(self):
        old_ip = self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True)
        old_ip = old_ip.split("/")
        old_ip[-1] = "24"
        old_ip = "/".join(old_ip)

        self.injector.recover_ip_change(
            host_name=self.faulty_device,
            old_ip=self.kathara_api.get_host_ip(self.faulty_device, "eth0", with_prefix=True),
            new_ip=old_ip,
            intf_name="eth0",
            old_gateway=self.kathara_api.get_default_gateway(self.faulty_device),
        )


class HostIncorrectNetmaskDetection(HostIncorrectNetmaskBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectNetmaskBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectNetmaskBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostIncorrectNetmaskLocalization(HostIncorrectNetmaskBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectNetmaskBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectNetmaskBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostIncorrectNetmaskBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class HostIncorrectNetmaskRCA(HostIncorrectNetmaskBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectNetmaskBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectNetmaskBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=HostIncorrectNetmaskBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectNetmaskBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
# Problem: Incorrect Host DNS resolvers
# =========================================


class HostIncorrectDNSBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_incorrect_dns"

    faulty_device = "host_1_1_1_1"
    symptom_desc = "Some hosts are unable to access web services."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_dns_misconfiguration(
            host_name=self.faulty_device,
        )

    def recover_fault(self):
        self.injector.recover_dns_misconfiguration(
            host_name=self.faulty_device,
            original_dns_ip=self.net_env.dns_ip,
        )


class HostIncorrectDNSDetection(HostIncorrectDNSBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectDNSBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostIncorrectDNSLocalization(HostIncorrectDNSBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectDNSBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostIncorrectDNSBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class HostIncorrectDNSRCA(HostIncorrectDNSBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostIncorrectDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectDNSBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=HostIncorrectDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostIncorrectDNSBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==========================================
# Problem: Host MAC address spoofing
# =========================================


class HostMACSpoofingBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    ROOT_CAUSE_NAME: str = "host_mac_spoofing"

    target_device_1 = "host_1_1_1_1"
    target_device_2 = "host_1_1_1_2"
    symptom_desc = "Some hosts experience intermittent connectivity issues."

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.spoofed_mac = "00:11:22:33:44:55"

    def inject_fault(self):
        self.kathara_api.exec_cmd(
            host_name=self.target_device_1,
            command=f"ifconfig eth0 hw ether {self.spoofed_mac}",
        )
        self.kathara_api.exec_cmd(
            host_name=self.target_device_2,
            command=f"ifconfig eth0 hw ether {self.spoofed_mac}",
        )

    def recover_fault(self):
        new_mac_1 = self.spoofed_mac.replace("55", "66")
        new_mac_2 = self.spoofed_mac.replace("55", "77")
        self.kathara_api.exec_cmd(
            host_name=self.target_device_1,
            command=f"ifconfig eth0 hw ether {new_mac_1}",
        )
        self.kathara_api.exec_cmd(
            host_name=self.target_device_2,
            command=f"ifconfig eth0 hw ether {new_mac_2}",
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    host_ip_conflict = HostMACSpoofingBase()
    host_ip_conflict.recover_fault()
