import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import (
    LocalizationSubmission,
    LocalizationTask,
)
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI


class FrrDownBase:
    """Base class for a FRR device down problem."""

    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    ROOT_CAUSE_NAME: str = "frr_service_down"

    failed_device: str = "router1"
    failed_service: str = "frr"
    symptom_desc = "Users report connectivity issues to other hosts in the network."

    def __init__(self):
        super().__init__()
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.failed_device, service_name=self.failed_service)
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.failed_device, service_name=self.failed_service)
        time.sleep(2)


class FrrDownDetection(FrrDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FrrDownBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class FrrDownLocalization(FrrDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FrrDownBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[FrrDownBase.failed_device],
    )

    def __init__(self):
        super().__init__()


class FrrDownRCA(FrrDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FrrDownBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=FrrDownBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=FrrDownBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    # Test the fault injection and recovery
    problem = FrrDownLocalization()
    print("Injecting fault...")
    problem.inject_fault()
