import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.intradomain_routing.ospf_multi_area.lab import OspfMultiArea
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaFRRAPI, KatharaNFTableAPI


class OspfAclBlockBaseTask:
    """Base class for a OSPF ACL block problem."""

    def __init__(self):
        self.net_env = OspfMultiArea()
        self.kathara_api = KatharaNFTableAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "OspfAclBlockBaseTask"
        self.problem_description = "A problem to detect OSPF ACL block in a host interface."
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        # Inject ACL rules to block OSPF (UDP port 89) traffic on router1
        self.injector.inject_acl_rule(
            host_name="router1",
            rule="ip protocol ospf drop",
            table_name="filter",
        )
        self.injector.inject_acl_rule(
            host_name="router1",
            rule="ip protocol ospf drop",
            table_name="filter",
        )
        # wait for a while to let ospf rules disappear
        time.sleep(10)

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name="router1", table_name="filter")
        # wait for a while to let ospf recover
        time.sleep(10)


class OspfAclBlockDetection(OspfAclBlockBaseTask, DetectionTask):
    def __init__(self):
        OspfAclBlockBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "OspfAclBlockDetection"
        self.problem_description = "Detection problem to identify if there is OSPF ACL block."


class OspfMisconfigBaseTask:
    """Base class for a OSPF area misconfiguration problem."""

    def __init__(self):
        self.net_env = OspfMultiArea()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)

        self.problem_name = "OspfAreaMisconfigBaseTask"
        self.problem_description = "OSPF area misconfiguration problem."
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_ospf_area_misconfig(host_name="router1", correct_area=0, wrong_area=66)
        # wait for a while to let ospf reconverge
        time.sleep(10)

    def recover_fault(self):
        self.injector.recover_ospf_area_misconfig(host_name="router1", correct_area=0, wrong_area=66)
        # wait for a while to let ospf recover
        time.sleep(10)


class OspfMisconfigDetection(OspfMisconfigBaseTask, DetectionTask):
    def __init__(self):
        OspfMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)
        self.problem_name = "OspfMisconfigDetection"
        self.problem_description = "Detection problem to identify if there is OSPF area misconfiguration."


if __name__ == "__main__":
    task = OspfMisconfigBaseTask()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
