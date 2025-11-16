import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.orchestrator.problems.config_host_error.host_error import HostPrefixErrorBaseTask
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.rca import LocalizationSubmission, LocalizationTask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
""" Problem: High link latency causing performance degradation """


class LinkLatencyBaseTask:
    DEFAULT_DEVICE = "router_"
    DEFAULT_DEVICE_INTF = "eth2"
    PROBLEM_ID = "link_latency"

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

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


class LinkFailureDetectionTask(LinkLatencyBaseTask, DetectionTask):
    META = ProblemMeta(
        id=f"{LinkLatencyBaseTask.PROBLEM_ID}_detection",
        description="Detection problem to identify if there is a link failure.",
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        root_cause_name=META.id,
    )

    def __init__(self):
        HostPrefixErrorBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class LinkFailureLocalization(LinkLatencyBaseTask, LocalizationTask):
    META = ProblemMeta(
        id=f"{LinkLatencyBaseTask.PROBLEM_ID}_localization",
        description="Localization a link failure.",
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        root_cause_category=RootCauseCategory.DEVICE_FAILURE,
        root_cause_name=META.id,
        target_component_ids=[LinkLatencyBaseTask.DEFAULT_DEVICE, LinkLatencyBaseTask.DEFAULT_DEVICE_INTF],
    )

    def __init__(self):
        LinkLatencyBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = LinkLatencyBaseTask()
    # task.inject_fault()
    # Here you would typically run your detection logic
    task.recover_fault()
