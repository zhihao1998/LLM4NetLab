from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.simple_bmv2.lab import SimpleBmv2
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaBaseAPI


class Bmv2DownBaseTask:
    """Base class for a Bmv2 device down problem."""

    def __init__(self):
        self.net_env = SimpleBmv2()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)

        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_bmv2_down(host_name="s1")

    def recover_fault(self):
        self.injector.recover_bmv2_down(host_name="s1")


class Bmv2DownDetection(Bmv2DownBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bmv2_down_detection",
        description="Detection problem to identify if there is a down bmv2 device.",
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        problem_level=TaskLevel.DETECTION,
    )
