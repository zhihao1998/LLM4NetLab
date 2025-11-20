"""Define and query information about an Detection task."""

import textwrap

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


RCA_TASK_INSTRUCTION = """\
            The network you are working with is described below:
            {net_desc}

            The following symptoms have been observed in the network:
            {symptom_desc}

            Your task is to perform root-cause analysis (RCA). Focus on *why* the anomaly occurs.
            Once you have determined the root cause, provide your conclusion for submission.
            """
RCA_TASK_INSTRUCTION_NO_SYMPTOM = """\
            The network you are working with is described below:
            {net_desc}

            Your task is to perform root-cause analysis (RCA). Focus on *why* the anomaly occurs.
            Once you have determined the root cause, provide your conclusion for submission.
            """


class RCATask(TaskBase):
    def __init__(self):
        super().__init__()
        self._task_desc_with_symptom = RCA_TASK_INSTRUCTION
        self._task_desc_no_symptom = RCA_TASK_INSTRUCTION_NO_SYMPTOM

    def task_desc(self, provide_symptom_desc: bool = False) -> str:
        if provide_symptom_desc:
            assert hasattr(self, "symptom_desc")
            tmpl = textwrap.dedent(self._task_desc_with_symptom)
            text = tmpl.format(
                net_desc=self.net_env.get_info(),
                symptom_desc=self.symptom_desc,
            ).strip()
            return text
        else:
            tmpl = textwrap.dedent(self._task_desc_no_symptom)
            text = tmpl.format(
                net_desc=self.net_env.get_info(),
            ).strip()
            return text

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

        gt_root_cause_category = getattr(self.get_submission(), "root_cause_category", "")
        gt_root_cause_name = getattr(self.get_submission(), "root_cause_name", "")
        accuracy = 0.0
        if root_cause_category == gt_root_cause_category:
            accuracy += 0.5
            if root_cause_name == gt_root_cause_name:
                accuracy += 0.5
        return accuracy

    def get_submission(self):
        assert self.root_cause_category and self.root_cause_name, (
            "Root cause category and name must be set in the task instance."
        )
        submission = RCASubmission(
            root_cause_category=self.root_cause_category,
            root_cause_name=self.root_cause_name,
        )
        return submission
