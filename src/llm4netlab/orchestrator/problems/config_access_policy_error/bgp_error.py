import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.service.kathara import KatharaNFTableAPI


class BGPAclBlockBaseTask:
    """Base class for a packet loss problem."""

    def __init__(self):
        self.net_env = SimpleBGP()  # each problem should tailor its own network environment
        self.kathara_api = KatharaNFTableAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

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


class BGPAclBlockDetection(BGPAclBlockBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_acl_block_detection",
        description="Detection problem to identify if there is BGP ACL block.",
        root_cause_category=RootCauseCategory.CONFIG_ACCESS_POLICY_ERROR,
        problem_level=TaskLevel.DETECTION,
    )
