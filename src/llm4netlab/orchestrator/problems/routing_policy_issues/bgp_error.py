import ipaddress
import logging
import re

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_service.lab import DCClosService
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.service.kathara import KatharaFRRAPI
from llm4netlab.service.kathara.base_api import KatharaBaseAPI

# ==================================================================
""" Problem: Base class for a BGP ASN misconfiguration problem. """
# ==================================================================


class BGPAsnMisconfigBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR
    root_cause_name: str = "bgp_asn_misconfig"

    faulty_router = "leaf_router_0_0"
    symptom_desc = "Some hosts are experiencing connectivity issues."

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        asn = self.kathara_api.exec_cmd(
            self.faulty_router, "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.inject_bgp_misconfig(
            host_name=self.faulty_router, correct_asn=as_number, wrong_asn=as_number + 600
        )

    def recover_fault(self):
        asn = self.kathara_api.exec_cmd(
            self.faulty_router, "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.recover_bgp_misconfig(
            host_name=self.faulty_router, correct_asn=as_number - 600, wrong_asn=as_number
        )


class BGPAsnMisconfigDetection(BGPAsnMisconfigBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=BGPAsnMisconfigBase.root_cause_category,
        root_cause_name=BGPAsnMisconfigBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class BGPAsnMisconfigLocalization(BGPAsnMisconfigBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPAsnMisconfigBase.root_cause_category,
        root_cause_name=BGPAsnMisconfigBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


# ==================================================================
""" Problem: Base class for a BGP missing route advertisement problem. """
# ==================================================================


class BGPMissingAdvertiseBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR
    root_cause_name: str = "bgp_missing_route_advertisement"

    faulty_router = "leaf_router_0_0"
    symptom_desc = "Some hosts are experiencing connectivity issues."

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        # find the line in frr.conf that broadcasts the network and comment it out
        self.injector.inject_bgp_remove_advertisement(host_name=self.faulty_router)

    def recover_fault(self):
        self.injector.recover_bgp_remove_advertisement(host_name=self.faulty_router)


class BGPMissingAdvertiseDetection(BGPMissingAdvertiseBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=BGPMissingAdvertiseBase.root_cause_category,
        root_cause_name=BGPMissingAdvertiseBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class BGPMissingAdvertiseLocalization(BGPMissingAdvertiseBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPMissingAdvertiseBase.root_cause_category,
        root_cause_name=BGPMissingAdvertiseBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class BGPMissingAdvertiseRCA(BGPMissingAdvertiseBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPMissingAdvertiseBase.root_cause_category,
        root_cause_name=BGPMissingAdvertiseBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
""" Problem: BGP static blackhole route misconfiguration problem. """
# ==================================================================


class StaticBlackHoleBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.END_HOST_MISCONFIGURATION
    root_cause_name: str = "host_static_blackhole"

    faulty_router = "leaf_router_1_0"
    target_device = "pc_0_0"
    symptom_desc = "The host is unable to reach certain networks."

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        host_network = ipaddress.ip_network(
            self.kathara_api.get_host_ip(self.target_device, with_prefix=True), strict=False
        )
        self.injector.inject_add_route_blackhole_nexthop(host_name=self.faulty_router, network=host_network)

    def recover_fault(self):
        host_network = ipaddress.ip_network(
            self.kathara_api.get_host_ip(self.target_device, with_prefix=True), strict=False
        )
        self.injector.recover_add_route_blackhole_nexthop(host_name=self.faulty_router, network=host_network)


class StaticBlackHoleDetection(StaticBlackHoleBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=StaticBlackHoleBase.root_cause_category,
        root_cause_name=StaticBlackHoleBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class StaticBlackHoleLocalization(StaticBlackHoleBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=StaticBlackHoleBase.root_cause_category,
        root_cause_name=StaticBlackHoleBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class StaticBlackHoleRCA(StaticBlackHoleBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=StaticBlackHoleBase.root_cause_category,
        root_cause_name=StaticBlackHoleBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
""" Problem: BGP blackhole route advertisement misconfiguration problem. """
# ==================================================================


class BGPBlackholeRouteLeakBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR
    root_cause_name: str = "bgp_blackhole_route_leak"

    faulty_device = "super_spine_router_0"
    target_device = "pc_0_0"

    def __init__(self):
        self.net_env = DCClosBGP()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        ip = self.kathara_api.get_host_ip(self.target_device, with_prefix=False)
        network_30 = ipaddress.ip_network(f"{ip}/30", strict=False)
        asn_number = self.kathara_api.exec_cmd(
            self.faulty_device, "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn_number)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.inject_add_route_blackhole_advertise(
            host_name=self.faulty_device, network=network_30, AS=as_number
        )

    def recover_fault(self):
        ip = self.kathara_api.get_host_ip(self.target_device, with_prefix=False)
        network_30 = ipaddress.ip_network(f"{ip}/30", strict=False)
        asn_number = self.kathara_api.exec_cmd(
            self.faulty_device, "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn_number)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.recover_add_route_blackhole_advertise(
            host_name=self.faulty_device, network=network_30, AS=as_number
        )


class BGPBlackholeRouteLeakDetection(BGPBlackholeRouteLeakBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=BGPBlackholeRouteLeakBase.root_cause_category,
        root_cause_name=BGPBlackholeRouteLeakBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class BGPBlackholeRouteLeakLocalization(BGPBlackholeRouteLeakBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPBlackholeRouteLeakBase.root_cause_category,
        root_cause_name=BGPBlackholeRouteLeakBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class BGPBlackholeRouteLeakRCA(BGPBlackholeRouteLeakBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPBlackholeRouteLeakBase.root_cause_category,
        root_cause_name=BGPBlackholeRouteLeakBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: BGP hijacking problem.
# ==================================================================


class BGPHijackingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR
    root_cause_name: str = "bgp_hijacking"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or DCClosService()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_device = [router for router in self.net_env.routers if "leaf" in router][0]
        web_server = self.net_env.servers["web"][-1]
        self.target_network = self.kathara_api.get_host_ip(web_server, with_prefix=True)
        self.target_network = str(
            ipaddress.ip_network(self.target_network, strict=False).subnets(new_prefix=25).__next__()
        )

    def inject_fault(self):
        asn_number = self.kathara_api.frr_get_bgp_asn_number(self.faulty_device)
        self.injector.inject_bgp_add_interface(
            host_name=self.faulty_device, intf_name="lo", ip_address=self.target_network
        )
        self.injector.inject_bgp_add_advertisement(
            host_name=self.faulty_device, network=self.target_network, AS=asn_number
        )

    def recover_fault(self):
        asn_number = self.kathara_api.frr_get_bgp_asn_number(self.faulty_device)
        self.injector.recover_bgp_add_advertisement(
            host_name=self.faulty_device, network=self.target_network, AS=asn_number
        )
        self.injector.recover_bgp_add_interface(
            host_name=self.faulty_device, intf_name="lo", ip_address=self.target_network
        )


class BGPHijackingDetection(BGPHijackingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=BGPHijackingBase.root_cause_category,
        root_cause_name=BGPHijackingBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class BGPHijackingLocalization(BGPHijackingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPHijackingBase.root_cause_category,
        root_cause_name=BGPHijackingBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class BGPHijackingRCA(BGPHijackingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPHijackingBase.root_cause_category,
        root_cause_name=BGPHijackingBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    task = BGPHijackingBase()
    # task.inject_fault()
    task.recover_fault()
