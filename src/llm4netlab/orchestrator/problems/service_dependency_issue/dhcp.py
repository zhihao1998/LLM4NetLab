import ipaddress
import logging

from llm4netlab.generator.fault.injector_service import FaultInjectorService
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterprise
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission, LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaBaseAPI

# ==================================================================
""" Problem: DHCP distributing incorrect gateway IP to hosts """
# ==================================================================


class DHCPWrongGatewayBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    ROOT_CAUSE_NAME: str = "dhcp_wrong_gateway"

    faulty_device = "dhcp_server"
    symptom_desc = "Some hosts are experiencing connectivity issues."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip("host_1_1_1_1", with_prefix=True), strict=False
            ).network_address
        )

        self.injector.inject_wrong_gateway(
            dhcp_server=self.faulty_device,
            subnet=subnet,
            wrong_gw=".".join(subnet.split(".")[:3] + ["254"]),
        )

    def recover_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip("host_1_1_1_1", with_prefix=True), strict=False
            ).network_address
        )
        self.injector.recover_wrong_gateway(
            dhcp_server=self.faulty_device,
            subnet=subnet,
            correct_gw=".".join(subnet.split(".")[:3] + ["1"]),
        )


class DHCPWrongGatewayDetection(DHCPWrongGatewayBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DHCPWrongGatewayBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongGatewayBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class DHCPWrongGatewayLocalization(DHCPWrongGatewayBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DHCPWrongGatewayBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongGatewayBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[DHCPWrongGatewayBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class DHCPWrongGatewayRCA(DHCPWrongGatewayBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DHCPWrongGatewayBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongGatewayBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=DHCPWrongGatewayBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongGatewayBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==================================================================
""" Problem: DHCP distributing incorrect DNS to hosts """
# ==================================================================


class DHCPWrongDNSBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    ROOT_CAUSE_NAME: str = "dhcp_wrong_dns"

    faulty_device = "dhcp_server"
    symptom_desc = "Some hosts can not access webservices."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip("host_1_1_1_1", with_prefix=True), strict=False
            ).network_address
        )

        self.injector.inject_wrong_dns(dhcp_server=self.faulty_device, subnet=subnet, wrong_dns="8.8.8.8")

    def recover_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip("host_1_1_1_1", with_prefix=True), strict=False
            ).network_address
        )
        dns_ip = self.kathara_api.get_host_ip("dns_server", with_prefix=False)
        self.injector.recover_wrong_dns(dhcp_server=self.faulty_device, subnet=subnet, correct_dns=dns_ip)


class DHCPWrongDNSDetection(DHCPWrongDNSBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DHCPWrongDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongDNSBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class DHCPWrongDNSLocalization(DHCPWrongDNSBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DHCPWrongDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongDNSBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[DHCPWrongDNSBase.faulty_device],
    )

    def __init__(self):
        super().__init__()


class DHCPWrongDNSRCA(DHCPWrongDNSBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DHCPWrongDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongDNSBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=DHCPWrongDNSBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=DHCPWrongDNSBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==================================================================
""" Problem: DHCP missing subnet configuration """
# ==================================================================


class DHCPMissingSubnetBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.SERVICE_DEPENDENCY_FAILURE
    ROOT_CAUSE_NAME: str = "dhcp_missing_subnet"

    faulty_device = "dhcp_server"
    symptom_desc = "Some hosts are experiencing connectivity issues."

    def __init__(self):
        self.net_env = OSPFEnterprise()
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)

    def inject_fault(self):
        subnet = str(
            ipaddress.ip_network(
                self.kathara_api.get_host_ip("host_1_1_1_1", with_prefix=True), strict=False
            ).network_address
        )
        self.injector.inject_delete_subnet(
            dhcp_server=self.faulty_device,
            subnet=subnet,
        )

    def recover_fault(self):
        self.injector.recover_deleted_subnet(
            dhcp_server=self.faulty_device,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = DHCPMissingSubnetBase()
    # problem.inject_fault()
    # To recover the fault, uncomment the following line
    problem.recover_fault()
