import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.orchestrator.problems.config_host_error.host_error import HostPrefixErrorBaseTask
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemLevel, ProblemMeta
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.rca import LocalizationSubmission, LocalizationTask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Link failure by ip link down on host interface """


class LinkFailureBaseTask:
    DEFAULT_DEVICE = "leaf_0_0"
    DEFAULT_DEVICE_INTF = "eth2"
    PROBLEM_ID = "link_failure"

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_intf_down(
            host_name=self.DEFAULT_DEVICE,
            intf_name=self.DEFAULT_DEVICE_INTF,
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_intf_down(
            host_name=self.DEFAULT_DEVICE,
            intf_name=self.DEFAULT_DEVICE_INTF,
        )
        time.sleep(2)


class LinkFailureDetectionTask(LinkFailureBaseTask, DetectionTask):
    META = ProblemMeta(
        id=f"{LinkFailureBaseTask.PROBLEM_ID}_detection",
        description="Detection problem to identify if there is a link failure.",
        issue_type=IssueType.DEVICE_FAILURE,
        problem_level=ProblemLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.DEVICE_FAILURE,
        problem_id=META.id,
    )

    def __init__(self):
        HostPrefixErrorBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class LinkFailureLocalization(LinkFailureBaseTask, LocalizationTask):
    META = ProblemMeta(
        id=f"{LinkFailureBaseTask.PROBLEM_ID}_localization",
        description="Localization a link failure.",
        issue_type=IssueType.DEVICE_FAILURE,
        problem_level=ProblemLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        issue_type=IssueType.DEVICE_FAILURE,
        problem_id=META.id,
        target_component_ids=[LinkFailureBaseTask.DEFAULT_DEVICE, LinkFailureBaseTask.DEFAULT_DEVICE_INTF],
    )

    def __init__(self):
        LinkFailureBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = LinkFailureBaseTask()
    # task.inject_fault()
    # Here you would typically run your detection logic
    task.recover_fault()
