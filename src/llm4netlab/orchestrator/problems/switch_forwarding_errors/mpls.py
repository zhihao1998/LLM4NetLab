import logging

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.net_env.p4.p4_mpls.lab import P4_MPLS
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

# ==================================================================
# Problem: MPLS Label Limit Exceeded
# ==================================================================


class P4MPLSLabelLimitExceededBase:
    root_cause_category = RootCauseCategory.SWITCH_FORWARDING_ERRORS
    root_case_name = "mpls_label_limit_exceeded"

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs) or P4_MPLS()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = self.net_env.bmv2_switches
        self.logger = logging.getLogger(__name__)

    def inject_fault(self):
        # replace the MPLS P4 program with one that has a lower label limit
        faulty_device = self.faulty_devices[0]
        self.kathara_api.exec_cmd(
            faulty_device,
            "cp mpls.p4 mpls.p4.bak && "
            "rm mpls.json && "
            "sed -Ei 's/#define[[:space:]]+CONST_MAX_LABELS[[:space:]]+10/#define CONST_MAX_LABELS 2/g' mpls.p4 ",
        )
        self.kathara_api.exec_cmd(faulty_device, "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            faulty_device,
            f"./hostlab/{faulty_device}.startup",
        )
        self.logger.info(f"Injected MPLS label limit exceeded fault on device: {faulty_device}")

    def recover_fault(self):
        # restore the original P4 program
        faulty_device = self.faulty_devices[0]
        self.kathara_api.exec_cmd(
            faulty_device,
            "mv mpls.p4.bak mpls.p4 ; rm mpls.json",
        )
        self.kathara_api.exec_cmd(faulty_device, "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            faulty_device,
            f"./hostlab/{faulty_device}.startup",
        )
        self.logger.info(f"Recovered MPLS label limit exceeded fault on device: {faulty_device}")


class P4MPLSLabelLimitExceededDetection(P4MPLSLabelLimitExceededBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4MPLSLabelLimitExceededBase.root_cause_category,
        root_cause_name=P4MPLSLabelLimitExceededBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4MPLSLabelLimitExceededLocalization(P4MPLSLabelLimitExceededBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4MPLSLabelLimitExceededBase.root_cause_category,
        root_cause_name=P4MPLSLabelLimitExceededBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4MPLSLabelLimitExceededRCA(P4MPLSLabelLimitExceededBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4MPLSLabelLimitExceededBase.root_cause_category,
        root_cause_name=P4MPLSLabelLimitExceededBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: MPLS Label Limit Exceeded
# ==================================================================


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = P4MPLSLabelLimitExceededBase(scenario_name="p4_mpls")
    # problem.recover_fault()
    problem.inject_fault()
