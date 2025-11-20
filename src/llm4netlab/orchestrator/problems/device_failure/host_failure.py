import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterpriseDHCP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Host crash simulated by pausing a docker instance """


class HostCrashBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    root_cause_name: str = "host_crash"

    faulty_device = "switch_dist_1_1"

    def __init__(self):
        self.net_env = OSPFEnterpriseDHCP()
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
        root_cause_category=HostCrashBase.root_cause_category,
        root_cause_name=HostCrashBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HostCrashLocalization(HostCrashBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HostCrashBase.root_cause_category,
        root_cause_name=HostCrashBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HostCrashRCA(HostCrashBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HostCrashBase.root_cause_category,
        root_cause_name=HostCrashBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    def __init__(self):
        super().__init__()
