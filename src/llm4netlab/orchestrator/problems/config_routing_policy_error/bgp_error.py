import time

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.service.kathara import KatharaFRRAPI


class BGPAsnMisconfigBaseTask:
    """Base class for a BGP ASN misconfiguration problem."""

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_bgp_misconfig(host_name="leaf_0_0", correct_asn=65200, wrong_asn=60000)
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_bgp_misconfig(host_name="leaf_0_0", correct_asn=65200, wrong_asn=60000)
        time.sleep(2)


class BGPAsnMisconfigDetection(BGPAsnMisconfigBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_asn_misconfig_detection",
        description="Detect if there is an anomaly in the network.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class BGPAsnMisconfigLocalization(BGPAsnMisconfigBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="bgp_asn_misconfig_localization",
        description="Localization problem to identify if there is BGP ASN misconfiguration.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        target_component_ids=["spine_0_0"],
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# ==============================================================


class BGPMissingRouteBaseTask:
    """Base class for a BGP missing route problem."""

    faulty_router = "leaf_0_0"

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        # find the line in frr.conf that broadcasts the network and comment it out
        self.injector.inject_bgp_missing_route(host_name=self.faulty_router)
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_bgp_missing_route(host_name=self.faulty_router)
        time.sleep(2)


class BGPMissingRouteDetection(BGPAsnMisconfigBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_missing_route_detection",
        description="Detect if there is an anomaly in the network.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class BGPMissingRouteLocalization(BGPAsnMisconfigBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="bgp_missing_route_localization",
        description=f"The BGP deamon of router {BGPMissingRouteBaseTask.faulty_router} is not working. The task is to localize this faulty device.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        target_component_ids=[BGPMissingRouteBaseTask.faulty_router],
    )

    def __init__(self):
        BGPAsnMisconfigBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# =============================================================

"""
Problem: Nexthop router shades the right route advertised via BGP
"""


class BGPBadNexthopBaseTask:
    DEFAULT_ROUTER = "spine_0_0"
    PROBLEM_DESC = ""

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_add_route_blackhole_nexthop(host_name=self.DEFAULT_ROUTER, network="10.0.0.0/24")
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_add_route_blackhole_nexthop(host_name=self.DEFAULT_ROUTER, network="10.0.0.0/24")
        time.sleep(2)


class BGPBadNexthopDetection(BGPBadNexthopBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_bad_nexthop_detection",
        description="Detection problem to identify if there is a bad BGP nexthop.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        root_cause_name=META.id,
    )

    def __init__(self):
        BGPBadNexthopBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class BGPBadNexthopLocalization(BGPBadNexthopBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="bgp_bad_nexthop_localization",
        description="Localization problem to identify if there is a bad BGP nexthop.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        root_cause_name=META.id,
        target_component_ids=[BGPBadNexthopBaseTask.DEFAULT_ROUTER],
    )

    def __init__(self):
        BGPBadNexthopBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# ===========================================================
# BGP remote blackhole, where a remote router advertises a blackhole route via BGP


class BGPRemoteBlackholeBaseTask:
    DEFAULT_ROUTER = "super_spine_0"

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        self.injector.inject_add_route_blackhole_advertise(
            host_name=self.DEFAULT_ROUTER, network="10.0.0.0/30", AS="65000"
        )
        time.sleep(2)

    def recover_fault(self):
        self.injector.recover_add_route_blackhole_advertise(
            host_name=self.DEFAULT_ROUTER, network="10.0.0.0/30", AS="65000"
        )
        time.sleep(2)


class BGPRemoteBlackholeDetection(BGPRemoteBlackholeBaseTask, DetectionTask):
    META = ProblemMeta(
        id="bgp_remote_blackhole_detection",
        description="Detection problem to identify if there is a remote blackhole route advertised via BGP.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        BGPRemoteBlackholeBaseTask.__init__(self)
        DetectionTask.__init__(self, self.net_env)


class BGPRemoteBlackholeLocalization(BGPRemoteBlackholeBaseTask, LocalizationTask):
    META = ProblemMeta(
        id="bgp_remote_blackhole_localization",
        description="Localization problem to identify if there is a remote blackhole route advertised via BGP.",
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        problem_level=TaskLevel.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        root_cause_category=RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR,
        root_cause_name=META.id,
        target_component_ids=[BGPRemoteBlackholeBaseTask.DEFAULT_ROUTER],
    )

    def __init__(self):
        BGPRemoteBlackholeBaseTask.__init__(self)
        LocalizationTask.__init__(self, self.net_env)


# ===========================================================
# BGP conflict route, where two routers advertise the same route via BGP with different nexthops


class BGPConflictRouteBaseTask:
    DEFAULT_ROUTER_1 = "leaf_0_0"
    DEFAULT_ROUTER_2 = "leaf_0_1"

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        res = self.kathara_api.frr_add_route(device_name=self.DEFAULT_ROUTER_2, route="10.0.0.0/24", next_hop="eth2")
        res = self.kathara_api.frr_add_bgp_advertisement(
            device_name=self.DEFAULT_ROUTER_2, network="10.0.0.0/24", as_path="65201"
        )
        time.sleep(2)

    def recover_fault(self):
        res = self.kathara_api.frr_del_route(device_name=self.DEFAULT_ROUTER_2, route="10.0.0.0/24", next_hop="eth2")
        res = self.kathara_api.frr_del_bgp_advertisement(
            device_name=self.DEFAULT_ROUTER_2, network="10.0.0.0/24", as_path="65201"
        )
        time.sleep(2)


if __name__ == "__main__":
    task = BGPMissingRouteBaseTask()
    task.inject_fault()
    # perform detection steps...
    # task.recover_fault()
