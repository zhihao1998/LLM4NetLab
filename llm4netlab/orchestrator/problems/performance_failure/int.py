from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.p4_int.lab import P4INTLab
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaTCAPI


class P4IntHopDelayHighBaseTask:
    """Base class for a P4 INT hop delay high problem."""

    def __init__(self):
        self.net_env = P4INTLab()
        self.kathara_api = KatharaTCAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "P4IntHopDelayHighBaseTask"
        self.problem_description = "A problem to detect high hop delay via the INT signals"
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        # Inject fault to simulate high hop delay
        self.injector.inject_delay(host_name="leaf1", interface="eth0", delay=1000)

    def recover_fault(self):
        self.injector.recover_delay(host_name="leaf1", interface="eth0")


class P4IntHopDelayHighDetection(P4IntHopDelayHighBaseTask, DetectionTask):
    def __init__(self):
        P4IntHopDelayHighBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "P4IntHopDelayHighDetection"
        self.problem_description = "Detection problem to identify if there is high hop delay via the INT signals"


if __name__ == "__main__":
    task = P4IntHopDelayHighDetection()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
