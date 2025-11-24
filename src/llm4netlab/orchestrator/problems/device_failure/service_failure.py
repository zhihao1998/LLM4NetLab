import logging
import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.net_env.p4.p4_bloom_filter.lab import P4BloomFilter
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL, KatharaBaseAPI

logger = logging.getLogger(__name__)

# ==================================================================
# Problem: P4 switch device failure (bmv2 switch down)
# ==================================================================


class Bmv2SwitchDownBase:
    root_cause_category = RootCauseCategory.DEVICE_FAILURE
    root_case_name = "bmv2_switch_down"

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs) or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        self.injector.inject_bmv2_down(host_name=self.faulty_device)

    def recover_fault(self):
        self.injector.recover_bmv2_down(host_name=self.faulty_device)


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


# ==================================================================
# Problem: FRR service down on a router device
# ==================================================================


class FrrDownBase:
    """Base class for a FRR device down problem."""

    root_cause_category: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    root_cause_name: str = "frr_service_down"

    symptom_desc = "Users report connectivity issues to other hosts in the network."

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs) or SimpleBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.routers[0]

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.faulty_devices, service_name="frr")
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.faulty_devices, service_name="frr")
        time.sleep(2)


class FrrDownDetection(FrrDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_name=FrrDownBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class FrrDownLocalization(FrrDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_name=FrrDownBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class FrrDownRCA(FrrDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_name=FrrDownBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = Bmv2SwitchDownBase()
    # problem.inject_fault()
    problem.recover_fault()
