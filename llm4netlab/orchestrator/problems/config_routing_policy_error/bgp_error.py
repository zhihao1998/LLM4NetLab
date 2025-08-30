import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemBase
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaFRRAPI


class BgpAsnMisconfigBaseTask:
    """Base class for a BGP ASN misconfiguration problem."""

    def __init__(self):
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_bgp_misconfig(host_name="router1", correct_asn=1, wrong_asn=2)
        time.sleep(5)

    def recover_fault(self):
        self.injector.recover_bgp_misconfig(host_name="router1", correct_asn=1, wrong_asn=2)
        time.sleep(5)


class BgpAsnMisconfigDetection(BgpAsnMisconfigBaseTask, DetectionTask):
    META = ProblemBase(
        id="bgp_asn_misconfig_detection",
        description="Detection problem to identify if there is BGP ASN misconfiguration.",
        issue_type="bgp_issue",
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_id=META.id,
    )

    def __init__(self):
        BgpAsnMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = BgpAsnMisconfigBaseTask()
    task.inject_fault()
    # perform detection steps...
    # task.recover_fault()
