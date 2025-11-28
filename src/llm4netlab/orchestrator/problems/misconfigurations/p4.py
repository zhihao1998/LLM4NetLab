import random

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger

logger = system_logger


# ==================================================================
# Problem: P4 aggressive detection thresholds of Bloom filter
# ==================================================================


class P4AggressiveDetectionThresholdsBase:
    root_cause_category = RootCauseCategory.NETWORK_NODE_ERROR
    root_cause_name = "p4_aggressive_detection_thresholds"
    TAGS: str = ["p4", "bloom_filter"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.bmv2_switches)]

    def inject_fault(self):
        # introduce a syntax error in the p4 file to simulate compilation error
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"cp {self.p4_name}.p4 {self.p4_name}.p4.bak && "
            f"rm {self.p4_name}.json && "
            f"sed -Ei 's/#define PACKET_THRESHOLD 1000/#define PACKET_THRESHOLD 100/g' {self.p4_name}.p4 ",
        )
        self.kathara_api.exec_cmd(self.faulty_devices[0], "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"./hostlab/{self.faulty_devices[0]}.startup",
        )

    def recover_fault(self):
        # restore the original p4 file
        self.kathara_api.exec_cmd(self.faulty_devices[0], f"cp {self.p4_name}.p4.bak {self.p4_name}.p4")
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "pkill -f simple_switch",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"./hostlab/{self.faulty_devices[0]}.startup",
        )


class P4AggressiveDetectionThresholdsDetection(P4AggressiveDetectionThresholdsBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4AggressiveDetectionThresholdsBase.root_cause_category,
        root_cause_name=P4AggressiveDetectionThresholdsBase.root_cause_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4AggressiveDetectionThresholdsLocalization(P4AggressiveDetectionThresholdsBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4AggressiveDetectionThresholdsBase.root_cause_category,
        root_cause_name=P4AggressiveDetectionThresholdsBase.root_cause_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4AggressiveDetectionThresholdsRCA(P4AggressiveDetectionThresholdsBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4AggressiveDetectionThresholdsBase.root_cause_category,
        root_cause_name=P4AggressiveDetectionThresholdsBase.root_cause_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )
