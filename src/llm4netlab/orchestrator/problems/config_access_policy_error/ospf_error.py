import time

from llm4netlab.net_env.kathara.intradomain_routing.ospf_multi_area.lab import OspfMultiArea

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaNFTableAPI


class OspfAclBlockBaseTask:
    """Base class for a OSPF ACL block problem."""

    def __init__(self):
        self.net_env = OspfMultiArea()
        self.kathara_api = KatharaNFTableAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

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
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name="router1", table_name="filter")
        # wait for a while to let ospf recover
        time.sleep(2)


class OspfAclBlockDetection(OspfAclBlockBaseTask, DetectionTask):
    META = ProblemMeta(
        id="ospf_acl_block_detection",
        description="Detect if there is an OSPF problem.",
        root_cause_category=RootCauseCategory.CONFIG_ACCESS_POLICY_ERROR,
        problem_level=TaskLevel.DETECTION,
    )


if __name__ == "__main__":
    task = OspfAclBlockBaseTask()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
