from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.simple_bmv2.lab import SimpleBmv2
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemLevel, ProblemMeta
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaBaseAPI


class Bmv2DownBaseTask:
    """Base class for a Bmv2 device down problem."""

    def __init__(self):
        self.net_env = SimpleBmv2()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)

        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_bmv2_down(host_name="s1")

    def recover_fault(self):
        self.injector.recover_bmv2_down(host_name="s1")


class Bmv2DownDetection(Bmv2DownBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bmv2_down_detection",
        description="Detection problem to identify if there is a down bmv2 device.",
        issue_type=IssueType.DEVICE_FAILURE,
        problem_level=ProblemLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.DEVICE_FAILURE,
        problem_id=META.id,
    )

    def __init__(self):
        Bmv2DownBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
