from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterprise
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==================================================================
""" Problem: DNS service down """
# ==================================================================


class DNSServiceDownBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    ROOT_CAUSE_NAME: str = "dns_service_down"

    faulty_device = "dns_server"
    symptom_desc = "Some hosts cannot access external websites."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.faulty_device, service_name="named")

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.faulty_device, service_name="named")


class DNSServiceDownDetection(DNSServiceDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSServiceDownBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class DNSServiceDownLocalization(DNSServiceDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSServiceDownBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[DNSServiceDownBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class DNSServiceDownRCA(DNSServiceDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSServiceDownBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=DNSServiceDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSServiceDownBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==================================================================
""" Problem: DNS listener port blocked """
# ==================================================================


class DNSPortBlockedBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    ROOT_CAUSE_NAME: str = "dns_port_blocked"

    faulty_device = "dns_server"
    symptom_desc = "Some hosts cannot access external websites."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_acl_rule(
            host_name=self.faulty_device,
            rule="tcp dport 53 drop",
            table_name="filter",
        )
        self.injector.inject_acl_rule(
            host_name=self.faulty_device,
            rule="udp dport 53 drop",
            table_name="filter",
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(
            host_name=self.faulty_device,
            table_name="filter",
        )
        self.injector.recover_acl_rule(
            host_name=self.faulty_device,
            table_name="filter",
        )


class DNSPortBlockedDetection(DNSPortBlockedBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSPortBlockedBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSPortBlockedBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class DNSPortBlockedLocalization(DNSPortBlockedBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSPortBlockedBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSPortBlockedBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[DNSPortBlockedBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class DNSPortBlockedRCA(DNSPortBlockedBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSPortBlockedBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSPortBlockedBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=DNSPortBlockedBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DNSPortBlockedBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()
