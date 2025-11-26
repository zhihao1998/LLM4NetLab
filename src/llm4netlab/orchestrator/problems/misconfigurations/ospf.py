import ipaddress
import logging
import random
import re

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import (
    LocalizationTask,
)
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaFRRAPI

# ==================================================================
# Problem: OSPF Area Misconfiguration
# ==================================================================


class OSPFAreaMisconfigBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "ospf_area_misconfiguration"

    TAGS: str = ["ospf"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.logger = logging.getLogger(__name__)
        self.faulty_devices = [random.choice(self.net_env.routers)]

    def inject_fault(self):
        correct_area = self.kathara_api.exec_cmd(
            self.faulty_router,
            "vtysh -c 'show running-config'",
        )
        pattern = re.compile(r"^\s*network\s+\S+\s+area\s+(\S+)", re.MULTILINE)
        m = pattern.search(correct_area)
        if not m:
            self.logger.error(f"Could not find OSPF area on {self.faulty_devices[0]}")
        correct_area = m.group(1)
        wrong_area = "66" if correct_area != "66" else "99"

        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"vtysh -c 'show running-config' | sed -E 's/(area )({correct_area})$/\\1{wrong_area}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(
            f"Injected OSPF area misconfiguration on {self.faulty_devices[0]} from area {correct_area} to {wrong_area}."
        )

    def recover_fault(self):
        server_subnet = str(
            ipaddress.ip_network(self.kathara_api.get_host_ip(self.faulty_devices[0], with_prefix=True), strict=False)
        )
        wrong_area = self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "vtysh -c 'show running-config'",
        )
        pattern = re.compile(rf"^\s*network\s+{re.escape(server_subnet)}\s+area\s+(\S+)\s*$", re.MULTILINE)
        m = pattern.search(wrong_area)
        if not m:
            raise ValueError(f"Could not find OSPF area for subnet {server_subnet} on {self.faulty_devices[0]}")
        wrong_area = m.group(1)
        correct_area = 0

        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"vtysh -c 'show running-config' | sed -E 's/(area )({wrong_area})$/\\1{correct_area}/' > /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(
            f"Recovered OSPF area misconfiguration on {self.faulty_devices[0]} from area {wrong_area} to {correct_area}."
        )


class OSPFAreaMisconfigDetection(OSPFAreaMisconfigBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=OSPFAreaMisconfigBase.root_cause_category,
        root_cause_name=OSPFAreaMisconfigBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class OSPFAreaMisconfigLocalization(OSPFAreaMisconfigBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=OSPFAreaMisconfigBase.root_cause_category,
        root_cause_name=OSPFAreaMisconfigBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class OSPFAreaMisconfigRCA(OSPFAreaMisconfigBase, RCATask):
    META = ProblemMeta(
        root_cause_category=OSPFAreaMisconfigBase.root_cause_category,
        root_cause_name=OSPFAreaMisconfigBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: OSPF Area Misconfiguration
# ==================================================================


class OSPFNeighborMissingBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.MISCONFIGURATION
    root_cause_name: str = "ospf_neighbor_missing"

    TAGS: str = ["ospf"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaFRRAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.logger = logging.getLogger(__name__)
        self.faulty_devices = [random.choice(self.net_env.routers)]

    def inject_fault(self):
        cmd = (
            "sed -i.bak -E "
            "'s|^([[:space:]]*)network[[:space:]]+[^[:space:]]+[[:space:]]+area|\\1# &|' "
            "/etc/frr/frr.conf"
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            cmd,
        )
        self.kathara_api.exec_cmd(self.faulty_devices[0], "systemctl restart frr")
        self.logger.info(f"Injected OSPF neighbor missing on {self.faulty_devices[0]}.")

    def recover_fault(self):
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "mv /etc/frr/frr.conf.bak /etc/frr/frr.conf && systemctl restart frr",
        )
        self.logger.info(f"Recovered OSPF neighbor missing on {self.faulty_devices[0]}.")


class OSPFNeighborMissingDetection(OSPFNeighborMissingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=OSPFNeighborMissingBase.root_cause_category,
        root_cause_name=OSPFNeighborMissingBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class OSPFNeighborMissingLocalization(OSPFNeighborMissingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=OSPFNeighborMissingBase.root_cause_category,
        root_cause_name=OSPFNeighborMissingBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class OSPFNeighborMissingRCA(OSPFNeighborMissingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=OSPFNeighborMissingBase.root_cause_category,
        root_cause_name=OSPFNeighborMissingBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    task = OSPFNeighborMissingBase()
    # task.inject_fault()
    # perform detection steps...
    task.recover_fault()
