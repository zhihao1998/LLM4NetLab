from llm4netlab.generator.fault.injector_tc import FaultInjectorTC
from llm4netlab.net_env.kathara.simple_bmv2.lab import SimpleBmv2
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaAPIALL


class P4PacketLossBaseTask:
    """Base class for a packet loss problem."""

    def __init__(self):
        self.net_env = SimpleBmv2()  # each problem should tailor its own network environment
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorTC(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        print("Injecting packet loss fault...")
        self.injector.inject_packet_loss(
            host_name="s3",
            interface="eth1",
            loss_percentage=90,
        )

    def recover_fault(self):
        print("Recovering from packet loss fault...")
        self.injector.recover_packet_loss(
            host_name="s3",
            interface="eth1",
        )


class P4PacketLossDetection(P4PacketLossBaseTask, DetectionTask):
    META = ProblemMeta(
        id="packet_loss_detection",
        description="Detect if there is packet loss in a host interface.",
        root_cause_category=RootCauseCategory.PERFORMANCE_DEGRADATION,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        root_cause_category=RootCauseCategory.PERFORMANCE_DEGRADATION,
        root_cause_name=META.id,
    )

    def __init__(self):
        P4PacketLossBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
