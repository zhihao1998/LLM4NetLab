import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.intradomain_routing.ospf_multi_area.lab import OspfMultiArea
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemBase
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaFRRAPI


class OspfMisconfigBaseTask:
    """Base class for a OSPF area misconfiguration problem."""

    def __init__(self):
        self.net_env = OspfMultiArea()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
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
    META = ProblemBase(
        id="ospf_misconfig_detection",
        description="Detect if there is an OSPF misconfiguration problem.",
        issue_type="ospf_issue",
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.CONFIG_ACCESS_POLICY_ERROR,
        problem_id=META.id,
    )

    def __init__(self):
        OspfMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = OspfMisconfigBaseTask()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
