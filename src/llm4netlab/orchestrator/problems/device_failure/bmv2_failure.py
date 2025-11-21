import logging

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.kathara.p4.p4_bloom_filter.lab import P4BloomFilter
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

logger = logging.getLogger(__name__)

# ==================================================================
# Problem: P4 switch device failure (bmv2 switch down)
# ==================================================================


class Bmv2SwitchDownBase:
    root_cause_category = RootCauseCategory.DEVICE_FAILURE
    root_case_name = "bmv2_switch_down"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        self.injector.inject_bmv2_down(host_name=self.failed_device)

    def recover_fault(self):
        self.injector.recover_bmv2_down(host_name=self.failed_device)


class Bmv2SwitchDownDetection(Bmv2SwitchDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=Bmv2SwitchDownBase.root_cause_category,
        root_cause_name=Bmv2SwitchDownBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class Bmv2SwitchDownLocalization(Bmv2SwitchDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=Bmv2SwitchDownBase.root_cause_category,
        root_cause_name=Bmv2SwitchDownBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class Bmv2SwitchDownRCA(Bmv2SwitchDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=Bmv2SwitchDownBase.root_cause_category,
        root_cause_name=Bmv2SwitchDownBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = Bmv2SwitchDownBase()
    # problem.inject_fault()
    problem.recover_fault()
