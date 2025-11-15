"""Define and query information about an Detection task."""

from textwrap import dedent

from pydantic import BaseModel, Field

from llm4netlab.orchestrator.tasks.base import TaskBase


class RCASubmission(BaseModel):
    root_cause_category: str = Field(
        ...,
        description=(
            dedent("""\
            High-level category of the root cause (e.g. 'config_host_error',
            'device_failure', 'performance_degradation').
            You MUST first call list_avail_root_cause_categories() and pick exactly 
            one value from the returned list.""")
        ),
    )
    root_cause_type: str = Field(
        ...,
        description=(
            dedent("""\
            Concrete root cause type within the selected category
            (e.g. 'bgp_asn_misconfiguration').
            After choosing root_cause_category, you MUST call
            list_avail_root_cause_types(root_cause_category) and pick exactly
            one value from the returned list.""")
        ),
    )


class RCATask(TaskBase):
    def __init__(self):
        super().__init__()
        self.task_desc = """\
            The network you are working with is described below:
            {net_desc}

            The following symptoms have been observed in the network (if any):
            {symptom_desc}

            Your task is to perform root-cause analysis (RCA). Focus on *why* the anomaly occurs.
            """

    def eval(self, submission: dict) -> float:
        """Evaluate the localization task submission.

        Args:
            submission: The submission to evaluate. Expected schema:
                {
                    "root_cause_category": str,
                    "root_cause_type": str,
                }

        Returns:
            float: The evaluation score in [0, 1], or -1.0 if submission is invalid.
        """
        root_cause_category = submission.get("root_cause_category", None)
        root_cause_type = submission.get("root_cause_type", None)

        # if there is no required field, return -1 score
        if root_cause_category is None or root_cause_type is None:
            return -1.0

        gt_root_cause_category = getattr(self.SUBMISSION, "root_cause_category", "")
        gt_root_cause_type = getattr(self.SUBMISSION, "root_cause_type", "")
        accuracy = 0.0
        if root_cause_category == gt_root_cause_category:
            accuracy += 0.5
            if root_cause_type == gt_root_cause_type:
                accuracy += 0.5
        return accuracy
