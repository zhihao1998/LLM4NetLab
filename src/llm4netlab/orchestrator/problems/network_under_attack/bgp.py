import ipaddress
import random

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: BGP hijacking problem.
# ==================================================================


class BGPHijackingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.NETWORK_UNDER_ATTACK
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
