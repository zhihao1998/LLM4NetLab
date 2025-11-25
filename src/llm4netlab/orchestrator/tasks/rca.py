"""Define and query information about an Detection task."""

import textwrap
from typing import List

from pydantic import BaseModel, Field

from llm4netlab.orchestrator.tasks.base import TaskBase


class RCASubmission(BaseModel):
    """
    The Root Cause Analysis (RCA) submission must use valid root cause names.
    Before submitting your answer, first query all available fault types by calling list_avail_problems().
    Your final submission must select one or more root_cause_names strictly from the options returned by that API.
    """

    root_cause_name: List[str] = Field(
        ...,
        description="The name(s) of the identified root cause(s) of the network anomaly.",
    )


RCA_TASK_INSTRUCTION = """\
            The network you are working with is described below:
            {net_desc}

            The following symptoms have been observed in the network:
            {symptom_desc}

            Your task is to perform root-cause analysis (RCA). Focus on *why* the anomaly occurs.
            Once you have determined the root cause (one or multiple), provide your conclusion for submission.
            """
RCA_TASK_INSTRUCTION_NO_SYMPTOM = """\
            The network you are working with is described below:
            {net_desc}

            There are some anomalies detected in the network.
            Your task is to perform root-cause analysis (RCA). Focus on *why* the anomaly occurs.
            Once you have determined the root cause (one or multiple), provide your conclusion for submission.
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
                    "root_cause_name": [str],  # List of identified root cause names
                }

        Returns:
            float: The evaluation score in [0, 1], or -1.0 if submission is invalid.
        """
        sub_rc_names = submission.get("root_cause_name", None)

        # if there is no required field, return -1 score
        if sub_rc_names is None:
            return -1.0

        # 3. Get ground truth components
        gt = self.get_submission()

        # 4. Get normalized component sets
        correct_rc_names = set([c for c in gt.root_cause_name])
        sub_rc_names = set([c for c in sub_rc_names])

        # 5. Calculate precision, recall, F1 score
        tp = len(correct_rc_names & sub_rc_names)
        fp = len(sub_rc_names - correct_rc_names)
        fn = len(correct_rc_names - sub_rc_names)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        accuracy = tp / len(correct_rc_names) if len(correct_rc_names) > 0 else 0.0

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)

        return round(float(accuracy), 4), round(float(precision), 4), round(float(recall), 4), round(float(f1), 4)

    def get_submission(self):
        assert self.root_cause_name, "Root cause name must be set in the task instance."
        if isinstance(self.root_cause_name, str):
            self.root_cause_name = [self.root_cause_name]
        submission = RCASubmission(
            root_cause_name=self.root_cause_name,
        )
        return submission
