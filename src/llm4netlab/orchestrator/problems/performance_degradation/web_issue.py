from llm4netlab.generator.fault.injector_service import FaultInjectorService
from llm4netlab.generator.fault.injector_tc import FaultInjectorTC
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_service.lab import DCClosService
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterprise
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import (
    LocalizationSubmission,
    LocalizationTask,
)
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaAPIALL


class DNSLookupLatencyBase:
    """Base class for DNS lookup latency problem."""

    root_cause_category: RootCauseCategory = RootCauseCategory.PERFORMANCE_DEGRADATION
    root_cause_name: str = "dns_lookup_latency"
    symptom_desc: str = "Users experience high latency when accessing web services."

    target_device: str = "dns_pod0"

    def __init__(self):
        super().__init__()
        self.net_env = DCClosService()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_delay(host_name=self.target_device, intf_name="eth0", delay_ms=1000)

    def recover_fault(self):
        self.injector.recover_delay(host_name=self.target_device, intf_name="eth0")


class DNSLookupLatencyDetection(DNSLookupLatencyBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class DNSLookupLatencyLocalization(DNSLookupLatencyBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[DNSLookupLatencyBase.target_device],
    )

    def __init__(self):
        super().__init__()


class DNSLookupLatencyRCA(DNSLookupLatencyBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=DNSLookupLatencyBase.root_cause_category,
        root_cause_name=DNSLookupLatencyBase.root_cause_name,
    )

    def __init__(self):
        super().__init__()


# ==================================================================
""" Problem: Web service under DoS attack causing performance degradation. """
# ==================================================================


class WebDoSBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.PERFORMANCE_DEGRADATION
    root_cause_name: str = "web_dos_attack"
    symptom_desc: str = "Users reports high latency when accessing some web services."

    target_device: str = "web_server0"
    attacker_device: str = "host_2_1_1_1"
    target_website: str = "web0.local"

    def __init__(self):
        super().__init__()
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_ab_attack(attacker_host=self.attacker_device, website=self.target_website)

    def recover_fault(self):
        self.injector.recover_ab_attack(attacker_host=self.attacker_device)


class WebDoSDetection(WebDoSBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class WebDoSLocalization(WebDoSBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[WebDoSBase.target_device],
    )

    def __init__(self):
        super().__init__()


class WebDoSRCA(WebDoSBase, RCATask):
    META = ProblemMeta(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
    )

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    # Test the fault injection and recovery
    problem = WebDoSBase()
    print("Injecting fault...")
    # problem.inject_fault()
    problem.recover_fault()
