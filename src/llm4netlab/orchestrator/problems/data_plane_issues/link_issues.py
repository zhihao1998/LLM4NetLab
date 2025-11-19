import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterprise
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Link fragmentation disabled, drop large packets """


class LinkFragBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    ROOT_CAUSE_NAME: str = "link_fragmentation_disabled"

    faulty_device = "switch_dist_1_1"
    faulty_intf = "eth0"
    symptom_desc = "Users report partial packet loss when communicating with other hosts."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_fragmentation_disabled(host_name=self.faulty_device, mtu=100)
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_link_frag_disabled(
            host_name=self.faulty_device,
        )
        time.sleep(2)


class LinkFragDetection(LinkFragBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=LinkFragBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFragBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class LinkFragLocalization(LinkFragBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=LinkFragBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFragBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[LinkFragBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class LinkFragRCA(LinkFragBase, RCATask):
    META = ProblemMeta(
        root_cause_category=LinkFragBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFragBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=LinkFragBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=LinkFragBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()
