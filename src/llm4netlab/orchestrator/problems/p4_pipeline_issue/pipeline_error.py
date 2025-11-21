import logging

from llm4netlab.generator.fault.injector_base import FaultInjectorBase
from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.kathara.p4.p4_bloom_filter.lab import P4BloomFilter
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta, RootCauseCategory, TaskDescription, TaskLevel
from llm4netlab.orchestrator.tasks.detection import DetectionTask
from llm4netlab.orchestrator.tasks.localization import LocalizationTask
from llm4netlab.orchestrator.tasks.rca import RCATask
from llm4netlab.service.kathara import KatharaAPIALL

logger = logging.getLogger(__name__)

# ==================================================================
# Problem: P4 parser misconfiguration
# ==================================================================


class P4ParserMisconfigBase:
    root_cause_category = RootCauseCategory.P4_PIPELINE_ISSUE
    root_case_name = "p4_parser_misconfiguration"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        # replace the 16 to 8 in "bit<16>   identification;" line to simulate misconfiguration
        self.kathara_api.exec_cmd(
            self.failed_device,
            "cp bloom_filter.p4 bloom_filter.p4.bak && "
            "rm bloom_filter.json && "
            "sed -Ei 's/bit<16>[[:space:]]+identification;/bit<8>   identification;/g' bloom_filter.p4 ",
        )
        self.kathara_api.exec_cmd(self.failed_device, "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.failed_device,
            f"./hostlab/{self.failed_device}.startup",
        )

    def recover_fault(self):
        # restore the original p4 file
        self.kathara_api.exec_cmd(self.failed_device, "cp bloom_filter.p4.bak bloom_filter.p4 && rm bloom_filter.json")
        self.kathara_api.exec_cmd(
            self.failed_device,
            "pkill -f simple_switch",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            f"./hostlab/{self.failed_device}.startup",
        )


class P4ParserMisconfigDetection(P4ParserMisconfigBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4ParserMisconfigBase.root_cause_category,
        root_cause_name=P4ParserMisconfigBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4ParserMisconfigLocalization(P4ParserMisconfigBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4ParserMisconfigBase.root_cause_category,
        root_cause_name=P4ParserMisconfigBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4ParserMisconfigRCA(P4ParserMisconfigBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4ParserMisconfigBase.root_cause_category,
        root_cause_name=P4ParserMisconfigBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: P4 compilation error due to header definition issue
# ==================================================================


class P4CompilationErrorHeaderBase:
    root_cause_category = RootCauseCategory.P4_PIPELINE_ISSUE
    root_case_name = "p4_compilation_error_header"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        # introduce a syntax error in the p4 file to simulate compilation error
        self.kathara_api.exec_cmd(
            self.failed_device,
            "cp bloom_filter.p4 bloom_filter.p4.bak && "
            "rm bloom_filter.json && "
            "sed -Ei 's/bit<16>[[:space:]]+identification;/bit<6>   identification;/g' bloom_filter.p4 ",
        )
        self.kathara_api.exec_cmd(self.failed_device, "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.failed_device,
            f"./hostlab/{self.failed_device}.startup",
        )

    def recover_fault(self):
        # restore the original p4 file
        self.kathara_api.exec_cmd(self.failed_device, "cp bloom_filter.p4.bak bloom_filter.p4")
        self.kathara_api.exec_cmd(
            self.failed_device,
            "pkill -f simple_switch",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            f"./hostlab/{self.failed_device}.startup",
        )


class P4CompilationErrorHeaderDetection(P4CompilationErrorHeaderBase, DetectionTask):
    META = ProblemMeta(
        root_cause_category=P4CompilationErrorHeaderBase.root_cause_category,
        root_cause_name=P4CompilationErrorHeaderBase.root_case_name,
        task_level=TaskLevel.DETECTION,
        description=TaskDescription.DETECTION,
    )


class P4CompilationErrorHeaderLocalization(P4CompilationErrorHeaderBase, LocalizationTask):
    META = ProblemMeta(
        root_cause_category=P4CompilationErrorHeaderBase.root_cause_category,
        root_cause_name=P4CompilationErrorHeaderBase.root_case_name,
        task_level=TaskLevel.LOCALIZATION,
        description=TaskDescription.LOCALIZATION,
    )


class P4CompilationErrorHeaderRCA(P4CompilationErrorHeaderBase, RCATask):
    META = ProblemMeta(
        root_cause_category=P4CompilationErrorHeaderBase.root_cause_category,
        root_cause_name=P4CompilationErrorHeaderBase.root_case_name,
        task_level=TaskLevel.RCA,
        description=TaskDescription.RCA,
    )


# ==================================================================
# Problem: P4 compilation error due to parser state issue
# ==================================================================


class P4CompilationErrorParserStateBase:
    root_cause_category = RootCauseCategory.P4_PIPELINE_ISSUE
    root_case_name = "p4_compilation_error_parser_state"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        # introduce a syntax error in the p4 file to simulate compilation error
        self.kathara_api.exec_cmd(
            self.failed_device,
            "cp bloom_filter.p4 bloom_filter.p4.bak && "
            "rm bloom_filter.json && "
            "sed -Ei 's/state ipv4/stete ipv4/g' bloom_filter.p4 ",
        )
        self.kathara_api.exec_cmd(self.failed_device, "pkill -f simple_switch")
        self.kathara_api.exec_cmd(
            self.failed_device,
            f"./hostlab/{self.failed_device}.startup",
        )

    def recover_fault(self):
        # restore the original p4 file
        self.kathara_api.exec_cmd(self.failed_device, "cp bloom_filter.p4.bak bloom_filter.p4")
        self.kathara_api.exec_cmd(
            self.failed_device,
            "pkill -f simple_switch",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            f"./hostlab/{self.failed_device}.startup",
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
    root_cause_category = RootCauseCategory.P4_PIPELINE_ISSUE
    root_case_name = "p4_table_entry_missing"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        # delete a table entry to simulate missing entry
        self.kathara_api.exec_cmd(
            self.failed_device,
            "simple_switch_CLI <<< 'table_clear MyIngress.ipv4_lpm'",
        )
        logger.info(f"Injected fault: Deleted table entries on {self.failed_device}")

    def recover_fault(self):
        # re-add the table entry
        self.kathara_api.exec_cmd(
            self.failed_device,
            "simple_switch_CLI <<< $(cat commands.txt)",
        )
        logger.info(f"Recovered fault: Re-added table entries on {self.failed_device}")


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
    root_cause_category = RootCauseCategory.P4_PIPELINE_ISSUE
    root_case_name = "p4_table_entry_misconfig"

    def __init__(self, net_env: NetworkEnvBase | None = None):
        super().__init__()
        self.net_env = net_env or P4BloomFilter()
        self.kathara_api = KatharaAPIALL(lab_name=self.net_env.lab.name)
        self.injector = FaultInjectorBase(lab_name=self.net_env.lab.name)
        self.failed_device = self.net_env.bmv2_switches[0]

    def inject_fault(self):
        # modify the entry in commands.txt to simulate misconfiguration by replacing the mac address
        self.kathara_api.exec_cmd(
            self.failed_device,
            "simple_switch_CLI <<< 'table_clear MyIngress.ipv4_lpm'",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            "sed -Ei.bak 's/00:00:0a:00:00:01/00:00:0a:00:00:66/g' commands.txt",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            "simple_switch_CLI <<< $(cat commands.txt)",
        )
        logger.info(f"Injected fault: Modified table entries on {self.failed_device}")

    def recover_fault(self):
        # restore the original commands.txt
        self.kathara_api.exec_cmd(
            self.failed_device,
            "simple_switch_CLI <<< 'table_clear MyIngress.ipv4_lpm'",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            "simple_switch_CLI <<< $(cat commands.txt.bak)",
        )
        self.kathara_api.exec_cmd(
            self.failed_device,
            "rm commands.txt.bak",
        )
        logger.info(f"Recovered fault: Restored table entries on {self.failed_device}")


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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    problem = P4TableEntryMisconfigBase()
    # problem.inject_fault()
    problem.recover_fault()
