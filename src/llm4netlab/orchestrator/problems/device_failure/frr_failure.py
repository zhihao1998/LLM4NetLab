from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import (
    DeviceComponent,
    LocalizationSubmission,
    LocalizationTask,
    ServiceComponent,
)
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI


class FrrDownBase:
    """Base class for a FRR device down problem."""

    root_cause_category: RootCauseCategory = RootCauseCategory.DEVICE_FAILURE
    root_cause_type: str = "frr_service_down"

    failed_device: str = "router1"
    failed_service: str = "frr"

    def __init__(self):
        super().__init__()
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.failed_device, service_name=self.failed_service)

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.failed_device, service_name=self.failed_service)


class FrrDownDetection(FrrDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_type=FrrDownBase.root_cause_type,
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
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_type=FrrDownBase.root_cause_type,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        target_components=[
            DeviceComponent(
                device_name=FrrDownBase.failed_device,
            ),
            ServiceComponent(
                service_name=FrrDownBase.failed_service,
            ),
        ],
    )

    def __init__(self):
        super().__init__()


class FrrDownRCA(FrrDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_type=FrrDownBase.root_cause_type,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=FrrDownBase.root_cause_category,
        root_cause_type=FrrDownBase.root_cause_type,
    )

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    # Test the fault injection and recovery
    problem = FrrDownLocalization()
    print("Injecting fault...")
    problem.inject_fault()
