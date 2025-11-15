import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.rca import LocalizationSubmission, LocalizationTask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: Link failure by ip link down on host interface """


class LinkFailureBaseTask:
    DEFAULT_DEVICE = "router1"
    DEFAULT_DEVICE_INTF = "eth0"
    PROBLEM_ID = "link_failure"

    def __init__(self):
        self.net_env = SimpleBGP()
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
        description="Detection problem to identify if there is anomaly in netwok.",
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        LinkFailureBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class LinkFailureLocalization(LinkFailureBaseTask, LocalizationTask):
    META = ProblemMeta(
        id=f"{LinkFailureBaseTask.PROBLEM_ID}_localization",
        description=f"Router {LinkFailureBaseTask.DEFAULT_DEVICE} has a link down on interface {LinkFailureBaseTask.DEFAULT_DEVICE_INTF}. Identify the device and interface.",
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        root_cause_type=META.id,
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
