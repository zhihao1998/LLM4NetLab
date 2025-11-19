import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterprise
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Host crash simulated by pausing a docker instance """


class HostCrashBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    ROOT_CAUSE_NAME: str = "host_crash"

    faulty_device = "switch_dist_1_1"

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_host_down(
            host_name=self.faulty_device,
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_host_down(
            host_name=self.faulty_device,
        )
        time.sleep(2)


class HostCrashDetection(HostCrashBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HostCrashBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostCrashBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class HostCrashLocalization(HostCrashBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostCrashBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostCrashBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[HostCrashBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class HostCrashRCA(HostCrashBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostCrashBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=HostCrashBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        root_cause_name=HostCrashBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()
