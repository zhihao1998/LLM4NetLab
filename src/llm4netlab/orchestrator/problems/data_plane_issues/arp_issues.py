import logging

from llm4netlab.generator.fault.injector_host import FaultInjectorHost
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: Arp cache poisoning causing data plane issues.
# ==================================================================

logger = logging.getLogger(__name__)


class ArpCachePoisoningBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.DATA_PLANE_ISSUE
    root_cause_name: str = "arp_cache_poisoning"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or OSPFEnterpriseStatic()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_device: str = self.net_env.hosts[0]

    def inject_fault(self):
        default_gateway = self.kathara_api.get_default_gateway(self.faulty_device)
        self.injector.inject_arp_misconfiguration(
            host_name=self.faulty_device,
            ip_address=default_gateway,
            fake_mac="00:11:22:33:44:55",
        )

    def recover_fault(self):
        default_gateway = self.kathara_api.get_default_gateway(self.faulty_device)
        self.injector.recover_arp_misconfiguration(
            host_name=self.faulty_device,
            ip_address=default_gateway,
        )


class ArpCachePoisoningDetection(ArpCachePoisoningBase):
    META = ProblemMeta(
        root_cause_category=ArpCachePoisoningBase.root_cause_category,
        root_cause_name=ArpCachePoisoningBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class ArpCachePoisoningLocalization(ArpCachePoisoningBase):
    META = ProblemMeta(
        root_cause_category=ArpCachePoisoningBase.root_cause_category,
        root_cause_name=ArpCachePoisoningBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class ArpCachePoisoningRCA(ArpCachePoisoningBase):
    META = ProblemMeta(
        root_cause_category=ArpCachePoisoningBase.root_cause_category,
        root_cause_name=ArpCachePoisoningBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: MAC address conflict
# ==================================================================


class MacAddressConflictBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.DATA_PLANE_ISSUE
    root_cause_name: str = "mac_address_conflict"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or OSPFEnterpriseStatic()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorHost(lab_name=self.net_env.lab.name)
        self.faulty_device: str = self.net_env.hosts[:2]

    def inject_fault(self):
        target_mac = self.kathara_api.get_host_mac_address(self.faulty_device[1], "eth0")
        self.kathara_api.exec_cmd(
            host_name=self.faulty_device[0],
            command=f"ip link set dev eth0 address {target_mac}",
        )
        logger.info(
            f"Injected MAC address conflict on {self.faulty_device[0]} with MAC {target_mac} of {self.faulty_device[1]}"
        )

    def recover_fault(self):
        random_mac = "12:34:56:78:9a:bb"
        self.kathara_api.exec_cmd(
            host_name=self.faulty_device[0],
            command=f"ip link set dev eth0 address {random_mac}",
        )
        logger.info(f"Recovered MAC address conflict on {self.faulty_device[0]} by setting MAC to {random_mac}")


class MacAddressConflictDetection(MacAddressConflictBase):
    META = ProblemMeta(
        root_cause_category=MacAddressConflictBase.root_cause_category,
        root_cause_name=MacAddressConflictBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class MacAddressConflictLocalization(MacAddressConflictBase):
    META = ProblemMeta(
        root_cause_category=MacAddressConflictBase.root_cause_category,
        root_cause_name=MacAddressConflictBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class MacAddressConflictRCA(MacAddressConflictBase):
    META = ProblemMeta(
        root_cause_category=MacAddressConflictBase.root_cause_category,
        root_cause_name=MacAddressConflictBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = MacAddressConflictBase()
    # problem.inject_fault()
    problem.recover_fault()
