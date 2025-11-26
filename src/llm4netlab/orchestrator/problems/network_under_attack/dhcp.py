import ipaddress
import random

from llm4netlab.generator.fault.injector_service import FaultInjectorService
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==================================================================
# Problem: DHCP distributing spoofed gateway to hosts
# ==================================================================


class DHCPSpoofedGatewayBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.NETWORK_UNDER_ATTACK
    root_cause_name: str = "dhcp_spoofed_gateway"

    TAGS: str = ["dhcp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["dhcp"])]
        self.faulty_devices.append(random.choice(self.net_env.hosts))

    def inject_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip(self.faulty_devices[1], with_prefix=True), strict=False
            ).network_address
        )

        self.injector.inject_wrong_gateway(
            dhcp_server=self.faulty_devices[0],
            subnet=subnet,
            wrong_gw=".".join(subnet.split(".")[:3] + ["254"]),
        )

    def recover_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip(self.faulty_devices[1], with_prefix=True), strict=False
            ).network_address
        )
        self.injector.recover_wrong_gateway(
            dhcp_server=self.faulty_devices[0],
            subnet=subnet,
            correct_gw=".".join(subnet.split(".")[:3] + ["1"]),
        )


class DHCPSpoofedGatewayDetection(DHCPSpoofedGatewayBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DHCPSpoofedGatewayBase.root_cause_category,
        root_cause_name=DHCPSpoofedGatewayBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DHCPSpoofedGatewayLocalization(DHCPSpoofedGatewayBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DHCPSpoofedGatewayBase.root_cause_category,
        root_cause_name=DHCPSpoofedGatewayBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DHCPSpoofedGatewayRCA(DHCPSpoofedGatewayBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DHCPSpoofedGatewayBase.root_cause_category,
        root_cause_name=DHCPSpoofedGatewayBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: DHCP distributing spoofed DNS to hosts
# ==================================================================


class DHCPSpoofedDNSBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.NETWORK_UNDER_ATTACK
    root_cause_name: str = "dhcp_spoofed_dns"

    symptom_desc = "Some hosts can not access webservices."
    TAGS: str = ["dhcp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["dhcp"])]
        self.faulty_devices.append(random.choice(self.net_env.hosts))

    def inject_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip(self.faulty_devices[1], with_prefix=True), strict=False
            ).network_address
        )

        self.injector.inject_wrong_dns(dhcp_server=self.faulty_devices[0], subnet=subnet, wrong_dns="8.8.8.8")

    def recover_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip(self.faulty_devices[1], with_prefix=True), strict=False
            ).network_address
        )
        dns_ip = self.kathara_api.get_host_ip("dns_server", with_prefix=False)
        self.injector.recover_wrong_dns(dhcp_server=self.faulty_devices[0], subnet=subnet, correct_dns=dns_ip)


class DHCPSpoofedDNSDetection(DHCPSpoofedDNSBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DHCPSpoofedDNSBase.root_cause_category,
        root_cause_name=DHCPSpoofedDNSBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DHCPSpoofedDNSLocalization(DHCPSpoofedDNSBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DHCPSpoofedDNSBase.root_cause_category,
        root_cause_name=DHCPSpoofedDNSBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DHCPSpoofedDNSRCA(DHCPSpoofedDNSBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DHCPSpoofedDNSBase.root_cause_category,
        root_cause_name=DHCPSpoofedDNSBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
""" Problem: DHCP missing subnet configuration """
# ==================================================================


class DHCPSpoofedSubnetBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.NETWORK_UNDER_ATTACK
    root_cause_name: str = "dhcp_spoofed_subnet"

    TAGS: str = ["dhcp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["dhcp"])]
        self.faulty_devices.append(random.choice(self.net_env.hosts))

    def inject_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip(self.faulty_devices[1], with_prefix=True), strict=False
            ).network_address
        )
        self.injector.inject_delete_subnet(
            dhcp_server=self.faulty_devices[0],
            subnet=subnet,
        )

    def recover_fault(self):
        self.injector.recover_deleted_subnet(
            dhcp_server=self.faulty_devices[0],
        )
