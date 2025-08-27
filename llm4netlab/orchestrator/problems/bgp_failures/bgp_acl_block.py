from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.discovery import DiscoveryTask
from llm4netlab.service.kathara import KatharaNFTableAPI


class BgpAclBlockBaseTask:
    """Base class for a packet loss problem."""

    def __init__(self):
        self.net_env = SimpleBGP()  # each problem should tailor its own network environment
        self.kathara_api = KatharaNFTableAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "PacketLossBaseTask"
        self.problem_description = "A problem to detect packet loss in a host interface."
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        print("Injecting fault: BGP ACL Block to discard all tcp port 179 traffic on router1")
        # Inject ACL rules to block BGP (TCP port 179) traffic on router1
        self.injector.inject_acl_rule(
            host_name="router1",
            rule="tcp dport 179 drop",
            table_name="filter",
        )
        self.injector.inject_acl_rule(
            host_name="router1",
            rule="tcp sport 179 drop",
            table_name="filter",
        )

    def recover_fault(self):
        print("Recovering from fault: Removing ACL rules on router1")
        self.injector.recover_acl_rule(host_name="router1", table_name="filter")


class BgpAclBlockDiscovery(BgpAclBlockBaseTask, DiscoveryTask):


class PacketLossDetection(PacketLossBaseTask, DetectionTask):
    def __init__(self):
        PacketLossBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "PacketLossDetection"
        self.problem_description = "Detection problem to identify which host interface is experiencing packet loss."
