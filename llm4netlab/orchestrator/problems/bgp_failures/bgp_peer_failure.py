import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaFRRAPI, KatharaNFTableAPI


class BgpAclBlockBaseTask:
    """Base class for a packet loss problem."""

    def __init__(self):
        self.net_env = SimpleBGP()  # each problem should tailor its own network environment
        self.kathara_api = KatharaNFTableAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "BgpAclBlockBaseTask"
        self.problem_description = "BGP ACL block problem."
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
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
        time.sleep(5)

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name="router1", table_name="filter")
        time.sleep(5)


class BgpAclBlockDetection(BgpAclBlockBaseTask, DetectionTask):
    def __init__(self):
        BgpAclBlockBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "BgpAclBlockDetection"
        self.problem_description = "Detection problem to identify if there is BGP problem."


class BgpAsnMisconfigBaseTask:
    """Base class for a BGP ASN misconfiguration problem."""

    def __init__(self):
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "BgpAsnMisconfigBaseTask"
        self.problem_description = "BGP ASN misconfiguration problem."
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_bgp_misconfig(host_name="router1", correct_asn=1, wrong_asn=2)
        time.sleep(5)

    def recover_fault(self):
        self.injector.recover_bgp_misconfig(host_name="router1", correct_asn=1, wrong_asn=2)
        time.sleep(5)


class BgpAsnMisconfigDetection(BgpAsnMisconfigBaseTask, DetectionTask):
    def __init__(self):
        BgpAsnMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "BgpAsnMisconfigDetection"
        self.problem_description = "Detection problem to identify if there is BGP ASN misconfiguration."


if __name__ == "__main__":
    task = BgpAsnMisconfigBaseTask()
    task.inject_fault()
    # perform detection steps...
    # task.recover_fault()
