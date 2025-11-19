import ipaddress
import logging
import re

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.kathara.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.orchestrator.tasks.localization import (
    LocalizationSubmission,
    LocalizationTask,
)
from llm4netlab.orchestrator.tasks.rca import RCASubmission, RCATask
from llm4netlab.service.kathara import KatharaFRRAPI

# ==================================================================
# Problem: OSPF Area Misconfiguration
# ==================================================================


class OSPFAreaMisconfigBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR
    ROOT_CAUSE_NAME: str = "ospf_area_misconfiguration"

    faulty_router: str = "switch_server_access"
    target_device: str = "web_server_0"

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.logger = logging.getLogger(__name__)

    def inject_fault(self):
        server_subnet = str(
            ipaddress.ip_network(self.kathara_api.get_host_ip(self.target_device, with_prefix=True), strict=False)
        )
        correct_area = self.kathara_api.exec_cmd(
            self.faulty_router,
            "vtysh -c 'show running-config'",
        )
        pattern = re.compile(rf"^\s*network\s+{re.escape(server_subnet)}\s+area\s+(\S+)\s*$", re.MULTILINE)
        m = pattern.search(correct_area)
        if not m:
            raise ValueError(f"Could not find OSPF area for subnet {server_subnet} on {self.faulty_router}")
        correct_area = m.group(1)
        wrong_area = "66" if correct_area != "66" else "99"

        self.kathara_api.exec_cmd(
            self.faulty_router,
            f"vtysh -c 'show running-config' | sed -E 's/(area )({correct_area})$/\\1{wrong_area}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(
            f"Injected OSPF area misconfiguration on {self.faulty_router} from area {correct_area} to {wrong_area}."
        )

    def recover_fault(self):
        server_subnet = str(
            ipaddress.ip_network(self.kathara_api.get_host_ip(self.target_device, with_prefix=True), strict=False)
        )
        wrong_area = self.kathara_api.exec_cmd(
            self.faulty_router,
            "vtysh -c 'show running-config'",
        )
        pattern = re.compile(rf"^\s*network\s+{re.escape(server_subnet)}\s+area\s+(\S+)\s*$", re.MULTILINE)
        m = pattern.search(wrong_area)
        if not m:
            raise ValueError(f"Could not find OSPF area for subnet {server_subnet} on {self.faulty_router}")
        wrong_area = m.group(1)
        correct_area = 0

        self.kathara_api.exec_cmd(
            self.faulty_router,
            f"vtysh -c 'show running-config' | sed -E 's/(area )({wrong_area})$/\\1{correct_area}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(
            f"Recovered OSPF area misconfiguration on {self.faulty_router} from area {wrong_area} to {correct_area}."
        )


class OSPFAreaMisconfigDetection(OSPFAreaMisconfigBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=OSPFAreaMisconfigBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFAreaMisconfigBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class OSPFAreaMisconfigLocalization(OSPFAreaMisconfigBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=OSPFAreaMisconfigBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFAreaMisconfigBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[OSPFAreaMisconfigBase.target_device],
    )

    def __init__(self):
        super().__init__()


class OSPFAreaMisconfigRCA(OSPFAreaMisconfigBase, RCATask):
    META = ProblemMeta(
        root_cause_category=OSPFAreaMisconfigBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFAreaMisconfigBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=OSPFAreaMisconfigBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFAreaMisconfigBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


# ==================================================================
# Problem: OSPF Area Misconfiguration
# ==================================================================


class OSPFNeighborMissingBase:
    ROOT_CAUSE_CATEGORY: RootCauseCategory = RootCauseCategory.CONFIG_ROUTING_POLICY_ERROR
    ROOT_CAUSE_NAME: str = "ospf_neighbor_missing"

    faulty_router: str = "switch_server_access"
    target_device: str = "web_server_0"

    def __init__(self):
        self.net_env = OSPFEnterpriseStatic()
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.logger = logging.getLogger(__name__)

    def inject_fault(self):
        server_subnet = str(
            ipaddress.ip_network(self.kathara_api.get_host_ip(self.target_device, with_prefix=True), strict=False)
        )
        cmd = (
            "sed -i.bak -E "
            f"'s|^([[:space:]]*)network[[:space:]]+{server_subnet}[[:space:]]+area|\\1# network {server_subnet} area|' "
            "/etc/frr/frr.conf"
        )
        self.kathara_api.exec_cmd(
            self.faulty_router,
            cmd,
        )
        self.kathara_api.exec_cmd(self.faulty_router, "systemctl restart frr")
        self.logger.info(f"Injected OSPF neighbor missing on {self.faulty_router}.")

    def recover_fault(self):
        self.kathara_api.exec_cmd(
            self.faulty_router,
            "mv /etc/frr/frr.conf.bak /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Recovered OSPF neighbor missing on {self.faulty_router}.")


class OSPFNeighborMissingDetection(OSPFNeighborMissingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=OSPFNeighborMissingBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFNeighborMissingBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
    )

    def __init__(self):
        super().__init__()


class OSPFNeighborMissingLocalization(OSPFNeighborMissingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=OSPFNeighborMissingBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFNeighborMissingBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )

    SUBMISSION = LocalizationSubmission(
        faulty_devices=[OSPFNeighborMissingBase.target_device],
    )

    def __init__(self):
        super().__init__()


class OSPFNeighborMissingRCA(OSPFNeighborMissingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=OSPFNeighborMissingBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFNeighborMissingBase.ROOT_CAUSE_NAME,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )

    SUBMISSION = RCASubmission(
        root_cause_category=OSPFNeighborMissingBase.ROOT_CAUSE_CATEGORY,
        root_cause_name=OSPFNeighborMissingBase.ROOT_CAUSE_NAME,
    )

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    task = OSPFNeighborMissingBase()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
