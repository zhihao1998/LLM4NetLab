from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.kathara.data_center_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: BGP Access Policy Misconfiguration - ACL blocking BGP traffic
# ==================================================================


class BGPAclBlockBase:
    root_cause_category = RootCauseCategory.ACCESS_POLICY_MISCONFIGURATION
    root_case_name = "bgp_acl_block"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        self.net_env = net_env or DCClosBGP()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.routers[0]

    def inject_fault(self):
        # Inject ACL rules to block BGP (TCP port 179) traffic on router1
        self.injector.inject_acl_rule(
            host_name=self.failed_device,
            rule="tcp dport 179 drop",
            table_name="filter",
        )
        self.injector.inject_acl_rule(
            host_name=self.failed_device,
            rule="tcp sport 179 drop",
            table_name="filter",
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name=self.failed_device, table_name="filter")


class BGPAclBlockDetection(BGPAclBlockBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=BGPAclBlockBase.root_cause_category,
        root_cause_name=BGPAclBlockBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class BGPAclBlockLocalization(BGPAclBlockBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=BGPAclBlockBase.root_cause_category,
        root_cause_name=BGPAclBlockBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class BGPAclBlockRCA(BGPAclBlockBase, RCATask):
    META = ProblemMeta(
        root_cause_category=BGPAclBlockBase.root_cause_category,
        root_cause_name=BGPAclBlockBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: OSPF Access Policy Misconfiguration - ACL blocking OSPF traffic
# ==================================================================


class OSPFAclBlockBase:
    root_cause_category = RootCauseCategory.ACCESS_POLICY_MISCONFIGURATION
    root_case_name = "ospf_acl_block"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        self.net_env = net_env or OSPFEnterpriseStatic()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.routers[0]

    def inject_fault(self):
        # Inject ACL rules to block OSPF (UDP port 89) traffic on router1
        self.injector.inject_acl_rule(
            host_name=self.failed_device,
            rule="ip protocol ospf drop",
            table_name="filter",
        )
        self.injector.inject_acl_rule(
            host_name=self.failed_device,
            rule="ip protocol ospf drop",
            table_name="filter",
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name=self.failed_device, table_name="filter")


class OSPFAclBlockDetection(OSPFAclBlockBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=OSPFAclBlockBase.root_cause_category,
        root_cause_name=OSPFAclBlockBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class OSPFAclBlockLocalization(OSPFAclBlockBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=OSPFAclBlockBase.root_cause_category,
        root_cause_name=OSPFAclBlockBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class OSPFAclBlockRCA(OSPFAclBlockBase, RCATask):
    META = ProblemMeta(
        root_cause_category=OSPFAclBlockBase.root_cause_category,
        root_cause_name=OSPFAclBlockBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: ARP Access Policy Misconfiguration - ACL blocking ARP traffic
# ==================================================================


class ARPAclBlockBase:
    root_cause_category = RootCauseCategory.ACCESS_POLICY_MISCONFIGURATION
    root_case_name = "arp_acl_block"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        self.net_env = net_env or OSPFEnterpriseStatic()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.hosts[0]

    def inject_fault(self):
        self.injector.inject_acl_rule(host_name=self.failed_device, rule="drop", table_name="filter", family="arp")
        self.kathara_api.exec_cmd(self.failed_device, "ip neigh flush all")

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name=self.failed_device, table_name="filter", family="arp")


class ARPAclBlockDetection(ARPAclBlockBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=ARPAclBlockBase.root_cause_category,
        root_cause_name=ARPAclBlockBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class ARPAclBlockLocalization(ARPAclBlockBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=ARPAclBlockBase.root_cause_category,
        root_cause_name=ARPAclBlockBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class ARPAclBlockRCA(ARPAclBlockBase, RCATask):
    META = ProblemMeta(
        root_cause_category=ARPAclBlockBase.root_cause_category,
        root_cause_name=ARPAclBlockBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: ARP Access Policy Misconfiguration - ACL blocking ICMP traffic
# ==================================================================


class IcmpAclBlockBase:
    root_cause_category = RootCauseCategory.ACCESS_POLICY_MISCONFIGURATION
    root_case_name = "icmp_acl_block"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        self.net_env = net_env or OSPFEnterpriseStatic()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.hosts[0]

    def inject_fault(self):
        self.injector.inject_acl_rule(
            host_name=self.failed_device, family="ip", rule="ip protocol icmp drop", table_name="filter"
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name=self.failed_device, table_name="filter", family="ip")


class IcmpAclBlockDetection(IcmpAclBlockBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=IcmpAclBlockBase.root_cause_category,
        root_cause_name=IcmpAclBlockBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class IcmpAclBlockLocalization(IcmpAclBlockBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=IcmpAclBlockBase.root_cause_category,
        root_cause_name=IcmpAclBlockBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class IcmpAclBlockRCA(IcmpAclBlockBase, RCATask):
    META = ProblemMeta(
        root_cause_category=IcmpAclBlockBase.root_cause_category,
        root_cause_name=IcmpAclBlockBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: ARP Access Policy Misconfiguration - ACL blocking HTTP traffic
# ==================================================================


class HttpAclBlockBase:
    root_cause_category = RootCauseCategory.ACCESS_POLICY_MISCONFIGURATION
    root_case_name = "http_acl_block"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        self.net_env = net_env or OSPFEnterpriseStatic()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.hosts[0]

    def inject_fault(self):
        self.injector.inject_acl_rule(
            host_name=self.failed_device, family="inet", rule="tcp dport 80 drop", table_name="filter"
        )

    def recover_fault(self):
        self.injector.recover_acl_rule(host_name=self.failed_device, table_name="filter", family="inet")


class HttpAclBlockDetection(HttpAclBlockBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=HttpAclBlockBase.root_cause_category,
        root_cause_name=HttpAclBlockBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class HttpAclBlockLocalization(HttpAclBlockBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=HttpAclBlockBase.root_cause_category,
        root_cause_name=HttpAclBlockBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class HttpAclBlockRCA(HttpAclBlockBase, RCATask):
    META = ProblemMeta(
        root_cause_category=HttpAclBlockBase.root_cause_category,
        root_cause_name=HttpAclBlockBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    problem = HttpAclBlockBase()
    # problem.inject_fault()
    problem.recover_fault()
