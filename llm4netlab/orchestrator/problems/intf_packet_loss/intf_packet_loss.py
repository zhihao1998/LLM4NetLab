from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.simple_bmv2.lab import SimpleTC
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.discovery import DiscoveryTask
from llm4netlab.service.kathara import KatharaBMv2API, KatharaTCAPI


# inheritance from multiple APIs for current use case
class KatharaAPIBMv2TC(KatharaBMv2API, KatharaTCAPI):
    """Combined API for both BMv2 and TC functionalities in Kathara."""

    def __init__(self, lab_name: str):
        super().__init__(lab_name)


class PacketLossBaseTask:
    """Base class for a packet loss problem."""

    def __init__(self):
        self.net_env = SimpleTC()  # each problem should tailor its own network environment
        self.kathara_api = KatharaAPIBMv2TC(lab_name=self.net_env.lab.name)

        self.problem_name = "PacketLossBaseTask"
        self.problem_description = "A problem to detect packet loss in a host interface."
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        print("Injecting packet loss fault...")
        self.injector._inject(
            fault_type="packet_loss",
            host_name="s3",  # TODO: make this adjustable
            interface="eth1",
            loss_percentage=90,
        )


class PacketLossDiscovery(PacketLossBaseTask, DiscoveryTask):
    def __init__(self):
        PacketLossBaseTask.__init__(self)
        DiscoveryTask.__init__(self, self.net_env)
        self.problem_name = "PacketLossDiscovery"
        self.problem_description = "Basic discovery problem to understand the network environment"


class PacketLossDetection(PacketLossBaseTask, DetectionTask):
    def __init__(self):
        PacketLossBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "PacketLossDetection"
        self.problem_description = "Detection problem to identify which host interface is experiencing packet loss."
