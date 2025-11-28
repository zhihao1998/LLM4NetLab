import logging
import random

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaBaseAPI
from llm4netlab.utils.logger import system_logger

logger = system_logger


# ==================================================================
# Problem: DNS service down
# ==================================================================


class DNSServiceDownBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.LINK_FAILURE
    root_cause_name: str = "dns_service_down"

    faulty_devices = "dns_server"
    symptom_desc = "Some hosts cannot access external websites."
    TAGS: str = ["dns"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["dns"])]

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.faulty_devices[0], service_name="named")

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.faulty_devices[0], service_name="named")


class DNSServiceDownDetection(DNSServiceDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.root_cause_category,
        root_cause_name=DNSServiceDownBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DNSServiceDownLocalization(DNSServiceDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.root_cause_category,
        root_cause_name=DNSServiceDownBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DNSServiceDownRCA(DNSServiceDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DNSServiceDownBase.root_cause_category,
        root_cause_name=DNSServiceDownBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: DHCP service down
# ==================================================================


class DHCPServiceDownBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.LINK_FAILURE
    root_cause_name: str = "dhcp_service_down"

    TAGS: str = ["dhcp"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaBaseAPI(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["dhcp"])]

    def inject_fault(self):
        self.injector.inject_service_down(host_name=self.faulty_devices[0], service_name="isc-dhcp-server")

    def recover_fault(self):
        self.injector.recover_service_down(host_name=self.faulty_devices[0], service_name="isc-dhcp-server")


class DHCPServiceDownDetection(DHCPServiceDownBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=DHCPServiceDownBase.root_cause_category,
        root_cause_name=DHCPServiceDownBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class DHCPServiceDownLocalization(DHCPServiceDownBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=DHCPServiceDownBase.root_cause_category,
        root_cause_name=DHCPServiceDownBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class DHCPServiceDownRCA(DHCPServiceDownBase, RCATask):
    META = ProblemMeta(
        root_cause_category=DHCPServiceDownBase.root_cause_category,
        root_cause_name=DHCPServiceDownBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = DHCPServiceDownBase()
    # problem.inject_fault()
    problem.recover_fault()
