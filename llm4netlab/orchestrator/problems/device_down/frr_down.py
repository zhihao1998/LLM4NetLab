from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaBaseAPI


class FrrDownBaseTask:
    """Base class for a FRR device down problem."""

    def __init__(self):
        self.net_env = SimpleBGP()  # each problem should tailor its own network environment
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "FrrDownBaseTask"
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_service_down(host_name="router1", service_name="frr")

    def recover_fault(self):
        self.injector.recover_service_down(host_name="router1", service_name="frr")


class FrrDownDetection(FrrDownBaseTask, DetectionTask):
    def __init__(self):
        FrrDownBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "FrrDownDetection"
