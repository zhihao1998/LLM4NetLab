import logging
import random

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

logger = logging.getLogger(__name__)

# ==================================================================
# Problem: P4 header definition error
# ==================================================================


class P4HeaderDefinitionErrorBase:
    root_cause_category = RootCauseCategory.NETWORK_NODE_ERROR
    root_case_name = "p4_header_definition_error"
    TAGS: str = ["p4"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.bmv2_switches)]
        # get the p4 program name
        self.p4_name = self.kathara_api.exec_cmd(self.faulty_devices[0], "echo *.p4 | sed 's/\\.p4//'")

    def inject_fault(self):
        # introduce a syntax error in the p4 file to simulate compilation error
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"cp {self.p4_name}.p4 {self.p4_name}.p4.bak && "
            f"rm {self.p4_name}.json && "
            f"sed -Ei 's/bit<16>[[:space:]]+identification;/bit<6>   identification;/g' {self.p4_name}.p4 ",
        )
        self.kathara_api.exec_cmd(self.faulty_devices[0], "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"./hostlab/{self.faulty_devices[0]}.startup",
        )

    def recover_fault(self):
        # restore the original p4 file
        self.kathara_api.exec_cmd(self.faulty_devices[0], "cp {self.p4_name}.p4.bak {self.p4_name}.p4")
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "pkill -f simple_switch",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"./hostlab/{self.faulty_devices[0]}.startup",
        )


class P4CompilationErrorHeaderDetection(P4HeaderDefinitionErrorBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4HeaderDefinitionErrorBase.root_cause_category,
        root_cause_name=P4HeaderDefinitionErrorBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4CompilationErrorHeaderLocalization(P4HeaderDefinitionErrorBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4HeaderDefinitionErrorBase.root_cause_category,
        root_cause_name=P4HeaderDefinitionErrorBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4CompilationErrorHeaderRCA(P4HeaderDefinitionErrorBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4HeaderDefinitionErrorBase.root_cause_category,
        root_cause_name=P4HeaderDefinitionErrorBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: P4 compilation error due to parser state issue
# ==================================================================


class P4CompilationErrorParserStateBase:
    root_cause_category = RootCauseCategory.NETWORK_NODE_ERROR
    root_case_name = "p4_compilation_error_parser_state"
    TAGS: str = ["p4"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.bmv2_switches)]
        # get the p4 program name
        self.p4_name = self.kathara_api.exec_cmd(self.faulty_devices[0], "echo *.p4 | sed 's/\\.p4//'")

    def inject_fault(self):
        # introduce a syntax error in the p4 file to simulate compilation error
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"cp {self.p4_name}.p4 {self.p4_name}.p4.bak && "
            f"rm {self.p4_name}.json && "
            f"sed -Ei 's/state /states /g' {self.p4_name}.p4 ",
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


class P4CompilationErrorParserStateDetection(P4CompilationErrorParserStateBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4CompilationErrorParserStateBase.root_cause_category,
        root_cause_name=P4CompilationErrorParserStateBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4CompilationErrorParserStateLocalization(P4CompilationErrorParserStateBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4CompilationErrorParserStateBase.root_cause_category,
        root_cause_name=P4CompilationErrorParserStateBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4CompilationErrorParserStateRCA(P4CompilationErrorParserStateBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4CompilationErrorParserStateBase.root_cause_category,
        root_cause_name=P4CompilationErrorParserStateBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: P4 table entry missing
# ==================================================================


class P4TableEntryMissingBase:
    root_cause_category = RootCauseCategory.NETWORK_NODE_ERROR
    root_case_name = "p4_table_entry_missing"
    TAGS: str = ["p4"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.bmv2_switches)]

    def inject_fault(self):
        # delete a table entry to simulate missing entry
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "simple_switch_CLI <<< 'table_clear MyIngress.ipv4_lpm'",
        )
        logger.info(f"Injected fault: Deleted table entries on {self.faulty_devices[0]}")

    def recover_fault(self):
        # re-add the table entry
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "simple_switch_CLI <<< $(cat commands.txt)",
        )
        logger.info(f"Recovered fault: Re-added table entries on {self.faulty_devices[0]}")


class P4TableEntryMissingDetection(P4TableEntryMissingBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4TableEntryMissingBase.root_cause_category,
        root_cause_name=P4TableEntryMissingBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4TableEntryMissingLocalization(P4TableEntryMissingBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4TableEntryMissingBase.root_cause_category,
        root_cause_name=P4TableEntryMissingBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4TableEntryMissingRCA(P4TableEntryMissingBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4TableEntryMissingBase.root_cause_category,
        root_cause_name=P4TableEntryMissingBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: P4 table entry misconfig
# ==================================================================


class P4TableEntryMisconfigBase:
    root_cause_category = RootCauseCategory.NETWORK_NODE_ERROR
    root_case_name = "p4_table_entry_misconfig"
    TAGS: str = ["p4"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [self.net_env.bmv2_switches[0]]

    def inject_fault(self):
        # modify the entry in commands.txt to simulate misconfiguration by replacing the mac address
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "simple_switch_CLI <<< 'table_clear MyIngress.ipv4_lpm'",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "sed -Ei.bak 's/00:00:/66:66:/g' commands.txt",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "simple_switch_CLI <<< $(cat commands.txt)",
        )
        logger.info(f"Injected fault: Modified table entries on {self.faulty_devices[0]}")

    def recover_fault(self):
        # restore the original commands.txt
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "simple_switch_CLI <<< 'table_clear MyIngress.ipv4_lpm'",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "simple_switch_CLI <<< $(cat commands.txt.bak)",
        )
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "rm commands.txt.bak",
        )
        logger.info(f"Recovered fault: Restored table entries on {self.faulty_devices[0]}")


class P4TableEntryMisconfigDetection(P4TableEntryMisconfigBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4TableEntryMisconfigBase.root_cause_category,
        root_cause_name=P4TableEntryMisconfigBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4TableEntryMisconfigLocalization(P4TableEntryMisconfigBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4TableEntryMisconfigBase.root_cause_category,
        root_cause_name=P4TableEntryMisconfigBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4TableEntryMisconfigRCA(P4TableEntryMisconfigBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4TableEntryMisconfigBase.root_cause_category,
        root_cause_name=P4TableEntryMisconfigBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: MPLS Label Limit Exceeded
# ==================================================================


class P4MPLSLabelLimitExceededBase:
    root_cause_category = RootCauseCategory.NETWORK_NODE_ERROR
    root_case_name = "mpls_label_limit_exceeded"

    TAGS: str = ["mpls"]

    def __init__(self, scenario_name: str | None, **kwargs):
        super().__init__()
        self.net_env = get_net_env_instance(scenario_name, **kwargs)
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.faulty_devices = [random.choice(self.net_env.bmv2_switches)]
        self.logger = logging.getLogger(__name__)

    def inject_fault(self):
        # replace the MPLS P4 program with one that has a lower label limit
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "cp mpls.p4 mpls.p4.bak && "
            "rm mpls.json && "
            "sed -Ei 's/#define[[:space:]]+CONST_MAX_LABELS[[:space:]]+10/#define CONST_MAX_LABELS 2/g' mpls.p4 ",
        )
        self.kathara_api.exec_cmd(self.faulty_devices[0], "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"./hostlab/{self.faulty_devices[0]}.startup",
        )
        self.logger.info(f"Injected MPLS label limit exceeded fault on device: {self.faulty_devices[0]}")

    def recover_fault(self):
        # restore the original P4 program
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            "mv mpls.p4.bak mpls.p4 ; rm mpls.json",
        )
        self.kathara_api.exec_cmd(self.faulty_devices[0], "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.faulty_devices[0],
            f"./hostlab/{self.faulty_devices[0]}.startup",
        )
        self.logger.info(f"Recovered MPLS label limit exceeded fault on device: {self.faulty_devices[0]}")


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = P4TableEntryMisconfigBase()
    # problem.inject_fault()
    problem.recover_fault()
