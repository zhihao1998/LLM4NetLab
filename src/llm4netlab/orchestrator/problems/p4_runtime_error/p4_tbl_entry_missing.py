from llm4netlab.net_env.kathara.l2_basic_forwarding.lab import L2BasicForwarding
from llm4netlab.orchestrator.problems.problem_base import IssueType, ProblemLevel, ProblemMeta
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission, DetectionTask
from llm4netlab.service.kathara import KatharaBMv2API


class P4TableEntryMissingBase:
    def __init__(self):
        self.net_env = L2BasicForwarding()
        self.kathara_api = KatharaBMv2API(lab_name=self.net_env.lab.name)


class P4TableEntryMissingDetection(P4TableEntryMissingBase, DetectionTask):
    META = ProblemMeta(
        id="p4_table_entry_missing_detection",
        description="Detect if there is any missing P4 table entry.",
        issue_type=IssueType.P4_RUNTIME_ERROR,
        problem_level=ProblemLevel.DETECTION,
    )

    SUBMISSION = DetectionSubmission(
        is_anomaly=True,
        issue_type=IssueType.P4_RUNTIME_ERROR,
        problem_id=META.id,
    )

    def __init__(self):
        super().__init__()
