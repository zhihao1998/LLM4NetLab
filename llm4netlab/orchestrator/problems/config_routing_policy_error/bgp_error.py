import time

from llm4netlab.generator.fault.injector_kathara import KatharaBaseFaultInjector
from llm4netlab.net_env.kathara.interdomain_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemLevel, ProblemMeta
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.service.kathara import KatharaFRRAPI


class BGPAsnMisconfigBaseTask:
    """Base class for a BGP ASN misconfiguration problem."""

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_bgp_misconfig(host_name="leaf_router_0_0", correct_asn=65200, wrong_asn=60000)
        time.sleep(10)

    def recover_fault(self):
        self.injector.recover_bgp_misconfig(host_name="leaf_router_0_0", correct_asn=65200, wrong_asn=60000)
        time.sleep(10)


class BGPAsnMisconfigDetection(BGPAsnMisconfigBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_asn_misconfig_detection",
        description="Detection problem to identify if there is BGP ASN misconfiguration.",
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=ProblemLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_id=META.id,
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class BGPAsnMisconfigLocalization(BGPAsnMisconfigBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="bgp_asn_misconfig_localization",
        description="Localization problem to identify if there is BGP ASN misconfiguration.",
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=ProblemLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_id=META.id,
        target_component_id="spine_router_0_0",
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# ==============================================================


class BGPMissingRouteBaseTask:
    """Base class for a BGP missing route problem."""

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = KatharaBaseFaultInjector(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        # find the line in frr.conf that broadcasts the network and comment it out
        self.injector.inject_bgp_missing_route(host_name="leaf_router_0_0")
        time.sleep(10)

    def recover_fault(self):
        self.injector.recover_bgp_missing_route(host_name="leaf_router_0_0")
        time.sleep(10)


class BGPMissingRouteDetection(BGPAsnMisconfigBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_missing_route_detection",
        description="Detection problem to identify if there is a missing BGP route.",
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=ProblemLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_id=META.id,
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class BGPMissingRouteLocalization(BGPAsnMisconfigBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="bgp_missing_route_localization",
        description="Localization problem to identify if there is a missing BGP route.",
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=ProblemLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        issue_type=IssueType.CONFIG_ROUTING_POLICY_ERROR,
        problem_id=META.id,
        target_component_id="leaf_0_0",
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


if __name__ == "__main__":
    task = BGPMissingRouteBaseTask()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
