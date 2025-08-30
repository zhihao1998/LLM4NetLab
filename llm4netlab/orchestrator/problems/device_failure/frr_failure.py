from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemBase
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaBaseAPI


class FrrDownBaseTask:
    """Base class for a FRR device down problem."""

    def __init__(self):
        self.net_env = SimpleBGP()  # each problem should tailor its own network environment
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name="router1", service_name="frr")

    def recover_fault(self):
        self.injector.recover_service_down(host_name="router1", service_name="frr")


class FrrDownDetection(FrrDownBaseTask, DetectionTask):
    META = ProblemBase(
        id="frr_down_detection",
        description="Detect if there is a down FRR service.",
        issue_type=IssueType.DEVICE_FAILURE,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.DEVICE_FAILURE,
        problem_id=META.id,
    )

    def __init__(self):
        FrrDownBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
