import logging
import random

from llm4netlab.generator.fault.injector_service import FaultInjectorService
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import (
    LocalizationTask,
)
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger

# ==================================================================
# Problem: Web service under DoS attack
# ==================================================================


class WebDoSBase:
    root_cause_category: RootCauseCategory = RootCauseCategory.NETWORK_UNDER_ATTACK
    root_cause_name: str = "web_dos_attack"
    symptom_desc: str = "Users reports high latency when accessing some web services."
    TAGS: str = ["http"]

    def __init__(self, scenario_name: NetworkEnvBase, **kwargs):
        super().__init__()
        self.logger = system_logger
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorService(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.servers["web"])]

        self.attacker_device = self.net_env.hosts[-1]
        self.target_website = self.kathara_api.get_host_ip(self.faulty_devices[0], with_prefix=False)

    def inject_fault(self):
        self.injector.inject_ab_attack(attacker_host=self.attacker_device, website=self.target_website)

    def recover_fault(self):
        self.injector.recover_ab_attack(attacker_host=self.attacker_device)


class WebDoSDetection(WebDoSBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class WebDoSLocalization(WebDoSBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class WebDoSRCA(WebDoSBase, RCATask):
    META = ProblemMeta(
        root_cause_category=WebDoSBase.root_cause_category,
        root_cause_name=WebDoSBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


if __name__ == "__main__":
    # Test the fault injection and recovery
    logging.basicConfig(level=logging.INFO)
    problem = WebDoSBase(scenario_name="dc_clos_service")
    # problem.inject_fault()
    problem.recover_fault()
