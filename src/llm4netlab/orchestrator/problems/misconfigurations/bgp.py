import ipaddress
import logging
import random
import re

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
""" Problem: Base class for a BGP ASN misconfiguration problem. """
# ==================================================================


class BGPAsnMisconfigBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "bgp_asn_misconfig"
    TAGS: str = ["bgp"]

    symptom_desc = "Some hosts are experiencing connectivity issues."

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.routers)]

    def inject_fault(self):
        asn = self.kathara_api.exec_cmd(
            self.faulty_devices[0], "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.inject_bgp_misconfig(
            host_name=self.faulty_devices[0], correct_asn=as_number, wrong_asn=as_number + 600
        )

    def recover_fault(self):
        asn = self.kathara_api.exec_cmd(
            self.faulty_devices[0], "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.recover_bgp_misconfig(
            host_name=self.faulty_devices[0], correct_asn=as_number - 600, wrong_asn=as_number
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


class BGPAsnMisconfigRCA(BGPAsnMisconfigBase, RCATask):
    META = ProblemMeta(
        root_cause_category=BGPAsnMisconfigBase.root_cause_category,
        root_cause_name=BGPAsnMisconfigBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
""" Problem: Base class for a BGP missing route advertisement problem. """
# ==================================================================


class BGPMissingAdvertiseBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "bgp_missing_route_advertisement"
    TAGS: str = ["bgp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.routers)]

    def inject_fault(self):
        # find the line in frr.conf that broadcasts the network and comment it out
        self.injector.inject_bgp_remove_advertisement(host_name=self.faulty_devices[0])

    def recover_fault(self):
        self.injector.recover_bgp_remove_advertisement(host_name=self.faulty_devices[0])


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


class BGPMissingAdvertiseRCA(BGPMissingAdvertiseBase, RCATask):
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
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "host_static_blackhole"
    TAGS: str = ["bgp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        for router in random.sample(self.net_env.routers, len(self.net_env.routers)):
            connected_devices = self.kathara_api.get_connected_devices(router)
            connected_hosts = [dev for dev in connected_devices if "switch" not in dev and "router" not in dev]
            if connected_hosts:
                self.faulty_devices = [router]
                self.victim_device = connected_hosts[0]
                self.victim_ip = self.kathara_api.get_host_ip(self.victim_device, with_prefix=False)
                break

    def inject_fault(self):
        host_network = ipaddress.ip_network(
            self.kathara_api.get_host_ip(self.victim_device, with_prefix=True), strict=False
        )
        self.injector.inject_add_route_blackhole_nexthop(host_name=self.faulty_devices[0], network=host_network)

    def recover_fault(self):
        host_ip = self.kathara_api.get_host_ip(self.victim_device, with_prefix=False)
        host_network = ipaddress.ip_network(host_ip, strict=False)
        self.injector.recover_add_route_blackhole_nexthop(host_name=self.faulty_devices[0], network=host_network)


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


class StaticBlackHoleRCA(StaticBlackHoleBase, RCATask):
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
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "bgp_blackhole_route_leak"
    TAGS: str = ["bgp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        for router in random.sample(self.net_env.routers, len(self.net_env.routers)):
            connected_devices = self.kathara_api.get_connected_devices(router)
            connected_hosts = [dev for dev in connected_devices if "switch" not in dev and "router" not in dev]
            if connected_hosts:
                self.faulty_devices = [router]
                self.victim_device = connected_hosts[0]
                self.victim_ip = self.kathara_api.get_host_ip(self.victim_device, with_prefix=False)
                break

    def inject_fault(self):
        network_30 = ipaddress.ip_network(f"{self.victim_ip}/30", strict=False)
        asn_number = self.kathara_api.exec_cmd(
            self.faulty_devices[0], "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn_number)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.inject_add_route_blackhole_advertise(
            host_name=self.faulty_devices[0], network=network_30, AS=as_number
        )

    def recover_fault(self):
        network_30 = ipaddress.ip_network(f"{self.victim_ip}/30", strict=False)
        asn_number = self.kathara_api.exec_cmd(
            self.faulty_devices[0], "vtysh -c 'show bgp summary' | grep 'BGP router identifier'"
        )
        match = re.search(r"local AS number\s+(\d+)", asn_number)
        if match:
            as_number = int(match.group(1))
        else:
            raise ValueError("Could not find AS number in BGP summary output")
        self.injector.recover_add_route_blackhole_advertise(
            host_name=self.faulty_devices[0], network=network_30, AS=as_number
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


class BGPBlackholeRouteLeakRCA(BGPBlackholeRouteLeakBase, RCATask):
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
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "bgp_hijacking"
    TAGS: str = ["bgp", "http"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.routers)]
        web_server = self.net_env.servers["web"][-1]
        self.target_network = self.kathara_api.get_host_ip(web_server, with_prefix=True)
        self.target_network = str(
            ipaddress.ip_network(self.target_network, strict=False).subnets(new_prefix=25).__next__()
        )

    def inject_fault(self):
        asn_number = self.kathara_api.frr_get_bgp_asn_number(self.faulty_devices)
        self.injector.inject_bgp_add_interface(
            host_name=self.faulty_devices[0], intf_name="lo", ip_address=self.target_network
        )
        self.injector.inject_bgp_add_advertisement(
            host_name=self.faulty_devices[0], network=self.target_network, AS=asn_number
        )

    def recover_fault(self):
        asn_number = self.kathara_api.frr_get_bgp_asn_number(self.faulty_devices)
        self.injector.recover_bgp_add_advertisement(
            host_name=self.faulty_devices[0], network=self.target_network, AS=asn_number
        )
        self.injector.recover_bgp_add_interface(
            host_name=self.faulty_devices[0], intf_name="lo", ip_address=self.target_network
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


class BGPHijackingRCA(BGPHijackingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=BGPHijackingBase.root_cause_category,
        root_cause_name=BGPHijackingBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    task = StaticBlackHoleBase(scenario_name="dc_clos_service")
    # task.inject_fault()
    task.recover_fault()
