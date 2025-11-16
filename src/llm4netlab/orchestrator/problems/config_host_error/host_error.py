import time

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==========================================
"""Problem: Missing IP address on host"""


class HostIPMissingBaseTask:
    DEFAULT_HOST = "pc1"

    def __init__(self):
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_remove_ip(host_name=self.DEFAULT_HOST, ip_address="10.0.0.2/24", intf_name="eth0")
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_remove_ip(host_name=self.DEFAULT_HOST, ip_address="10.0.0.2/24", intf_name="eth0")
        time.sleep(2)


class HostIPMissingDetectionTask(HostIPMissingBaseTask, DetectionTask):
    META = ProblemMeta(
        id="host_ip_missing_detection",
        description="Detect if there is an anomaly in the network.",
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        HostIPMissingBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class HostIPMissingLocalization(HostIPMissingBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="host_ip_missing_localization",
        description=f"The IP address is missing on host {HostIPMissingBaseTask.DEFAULT_HOST}. Identify the host.",
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        target_component_ids=[HostIPMissingBaseTask.DEFAULT_HOST],
    )

    def __init__(self):
        HostIPMissingBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# ==========================================
""" Problem: Missing default route on host """


class HostDefaultRouteMissingBaseTask:
    DEFAULT_HOST = "pc1"

    def __init__(self):
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_host_default_route_missing(host_name=self.DEFAULT_HOST)
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_host_default_route_missing(host_name=self.DEFAULT_HOST)
        time.sleep(2)


class HostDefaultRouteMissingDetectionTask(HostDefaultRouteMissingBaseTask, DetectionTask):
    META = ProblemMeta(
        id="host_default_route_missing_detection",
        description="Detection problem to identify if there is a missing default route on the host.",
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        HostDefaultRouteMissingBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class HostDefaultRouteMissingLocalization(HostDefaultRouteMissingBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="host_default_route_missing_localization",
        description="Localization problem to identify if there is a missing default route on the host.",
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        target_component_ids=[HostDefaultRouteMissingBaseTask.DEFAULT_HOST],
    )

    def __init__(self):
        HostDefaultRouteMissingBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# ==========================================
""" Problem: IP conflict on host TODO"""


# class HostIPConflictBaseTask:
#     DEFAULT_HOST_1 = "pc_0_3"
#     DEFAULT_HOST_2 = "pc_0_4"

#     def __init__(self):
#         self.net_env = DCClosBGP()
#         self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
#         self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

#     def inject_fault(self):
#         self.injector.inject_ip_change(
#             host_name=self.DEFAULT_HOST_2,
#             old_ip="10.0.3.4/24",
#             new_ip="10.0.3.2/24",
#             intf_name="eth0",
#             new_gateway="10.0.3.3",
#         )
#         time.sleep(2)

#     def recover_fault(self):
#         self.injector.recover_ip_change(
#             host_name=self.DEFAULT_HOST_2,
#             old_ip="10.0.3.4/24",
#             new_ip="10.0.3.2/24",
#             intf_name="eth0",
#             old_gateway="10.0.3.3",
#         )
#         time.sleep(2)

# ==========================================
""" Problem: IP prefix error on host """


class HostPrefixErrorBaseTask:
    DEFAULT_HOST = "pc1"

    def __init__(self):
        self.net_env = SimpleBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_ip_change(
            host_name=self.DEFAULT_HOST,
            old_ip="10.0.0.2/24",
            new_ip="10.0.0.4/30",
            intf_name="eth0",
            new_gateway="10.0.0.1",
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_ip_change(
            host_name=self.DEFAULT_HOST,
            old_ip="10.0.0.2/24",
            new_ip="10.0.0.4/30",
            intf_name="eth0",
            old_gateway="10.0.0.1",
        )
        time.sleep(2)


class HostPrefixErrorDetectionTask(HostPrefixErrorBaseTask, DetectionTask):
    META = ProblemMeta(
        id="host_prefix_error_detection",
        description="Detection problem to identify if there is an IP prefix error on the host.",
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        root_cause_name=META.id,
    )

    def __init__(self):
        HostPrefixErrorBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class HostPrefixErrorLocalization(HostPrefixErrorBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="host_prefix_error_localization",
        description="Localization problem to identify if there is an IP prefix error on the host.",
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        root_cause_category=RootCauseCategory.CONFIG_HOST_ERROR,
        root_cause_name=META.id,
        target_component_ids=[HostPrefixErrorBaseTask.DEFAULT_HOST],
    )

    def __init__(self):
        HostPrefixErrorBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = HostPrefixErrorDetectionTask()
    # task.inject_fault()
    # Here you would typically run your detection logic
    task.recover_fault()
