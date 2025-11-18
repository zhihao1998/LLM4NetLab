"""Define and query information about an Detection task."""

from pydantic import BaseModel, Field

from llm4netlab.orchestrator.tasks.base import TaskBase


class RCASubmission(BaseModel):
    """
    Schema for Root Cause Analysis (RCA) task submission.
    The input must be selected from list_avail_root_causes() API.
    """

    root_cause_category: str = Field(
        ...,
        description="High-level category of the root cause.",
    )
    root_cause_name: str = Field(
        ...,
        description="Concrete root cause name within the selected category.",
    )


class RCATask(TaskBase):
    def __init__(self):
        super().__init__()
        self.task_desc = """\
            The network you are working with is described below:
            {net_desc}

            The following symptoms have been observed in the network (no symptom does not mean no anomaly):
            {symptom_desc}

            Your task is to perform root-cause analysis (RCA). Focus on *why* the anomaly occurs.
            Once you have determined the root cause, provide your conclusion for submission.
            """

    def eval(self, submission: dict) -> float:
        """Evaluate the localization task submission.

        Args:
            submission: The submission to evaluate. Expected schema:
                {
                    "root_cause_category": str,
                    "root_cause_name": str,
                }

        Returns:
            float: The evaluation score in [0, 1], or -1.0 if submission is invalid.
        """
        root_cause_category = submission.get("root_cause_category", None)
        root_cause_name = submission.get("root_cause_name", None)

        # if there is no required field, return -1 score
        if root_cause_category is None or root_cause_name is None:
            return -1.0

        gt_root_cause_category = getattr(self.SUBMISSION, "root_cause_category", "")
        gt_root_cause_name = getattr(self.SUBMISSION, "root_cause_name", "")
        accuracy = 0.0
        if root_cause_category == gt_root_cause_category:
            accuracy += 0.5
            if root_cause_name == gt_root_cause_name:
                accuracy += 0.5
        return accuracy
