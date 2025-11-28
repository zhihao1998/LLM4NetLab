import logging
import random
from venv import logger

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL, KatharaBaseAPI
from llm4netlab.utils.logger import system_logger

logger = system_logger

# ==================================================================
# Problem: P4 switch device failure (bmv2 switch down)
# ==================================================================


class Bmv2SwitchDownBase:
    root_cause_category = RootCauseCategory.LINK_FAILURE
    root_cause_name = "bmv2_switch_down"
    TAGS: str = ["p4"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.bmv2_switches)]

    def inject_fault(self):
        self.injector.inject_bmv2_down(host_name=self.faulty_devices[0])

    def recover_fault(self):
        self.injector.recover_bmv2_down(host_name=self.faulty_devices[0])


class Bmv2SwitchDownDetection(Bmv2SwitchDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=Bmv2SwitchDownBase.root_cause_category,
        root_cause_name=Bmv2SwitchDownBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class Bmv2SwitchDownLocalization(Bmv2SwitchDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=Bmv2SwitchDownBase.root_cause_category,
        root_cause_name=Bmv2SwitchDownBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class Bmv2SwitchDownRCA(Bmv2SwitchDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=Bmv2SwitchDownBase.root_cause_category,
        root_cause_name=Bmv2SwitchDownBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: FRR service down on a router device
# ==================================================================


class FrrDownBase:
    """Base class for a FRR device down problem."""

    root_cause_category: RootCauseCategory = RootCauseCategory.NETWORK_NODE_ERROR
    root_cause_name: str = "frr_service_down"
    TAGS: str = ["frr"]

    symptom_desc = "Users report connectivity issues to other hosts in the network."

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.routers)]

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.faulty_devices[0], service_name="frr")

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.faulty_devices[0], service_name="frr")


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
