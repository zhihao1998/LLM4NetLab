import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.intradomain_routing.ospf_multi_area.lab import OspfMultiArea
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemBase
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaNFTableAPI


class OspfAclBlockBaseTask:
    """Base class for a OSPF ACL block problem."""

    def __init__(self):
        self.net_env = OspfMultiArea()
        self.kathara_api = KatharaNFTableAPI(lab_name=self.net_env.lab.name)
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
    META = ProblemBase(
        id="ospf_acl_block_detection",
        description="Detect if there is an OSPF problem.",
        issue_type="ospf_issue",
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.CONFIG_ACCESS_POLICY_ERROR,
        problem_id=META.id,
    )

    def __init__(self):
        OspfAclBlockBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = OspfAclBlockBaseTask()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
