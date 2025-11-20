"""Define and query information about an Detection task."""

import textwrap

from pydantic import BaseModel, Field, ValidationError

from llm4netlab.orchestrator.tasks.base import TaskBase


class LocalizationSubmission(BaseModel):
    faulty_devices: list[str] = Field(
        ...,
        description=textwrap.dedent("""\
            List of localized devices that are identified as faulty. Each item is a device name (string).
            Example: ["router_1", "switch_2"]
        """),
    )


LOCAL_TASK_INSTRUCTION = """\
            The network you are working with is described below:
            {net_desc}

            The following symptoms have been observed in the network (if any):
            {symptom_desc}

            Your task is to localize the anomaly.
            Pinpoint the faulty component(s), such as device, interface, link, prefix, neighbor, or path segment.
            Focus strictly on *where* the anomaly occurs.

            Do not analyze or speculate about root causes. Do not propose mitigations.
            Once you have identified the faulty component(s), provide your conclusion for submission.
            """

LOCAL_TASK_INSTRUCTION_NO_SYMPTOM = """\
            The network you are working with is described below:
            {net_desc}

            Your task is to localize the anomaly.
            Pinpoint the faulty component(s), such as device, interface, link, prefix, neighbor, or path segment.
            Focus strictly on *where* the anomaly occurs.

            Do not analyze or speculate about root causes. Do not propose mitigations.
            Once you have identified the faulty component(s), provide your conclusion for submission.
            """


class LocalizationTask(TaskBase):
    def __init__(self):
        super().__init__()
        self._task_desc_with_symptom = LOCAL_TASK_INSTRUCTION
        self._task_desc_no_symptom = LOCAL_TASK_INSTRUCTION_NO_SYMPTOM
        self.faulty_devices: list[str] = []

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
                    "faulty_devices": ["device1", "device2", ...]
                }

        Returns:
            float: The evaluation score in [0, 1], or -1.0 if submission is invalid.
        """
        # 1. Validate submission schema
        try:
            parsed_submission = LocalizationSubmission.model_validate(submission)
        except ValidationError:
            return -1.0

        submitted_components = parsed_submission.faulty_devices

        # 3. Get ground truth components
        gt = self.get_submission()
        gt_components_raw = gt.faulty_devices if gt else []

        # 4. Get normalized component sets
        correct_components = set([c for c in gt_components_raw])
        submitted_components_norm = set([c for c in submitted_components])

        # 5. Calculate precision, recall, F1 score
        tp = len(correct_components & submitted_components_norm)
        fp = len(submitted_components_norm - correct_components)
        fn = len(correct_components - submitted_components_norm)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)

        return float(f1)

    def get_submission(self):
        assert self.faulty_devices, "Faulty devices not set in the task instance."
        if isinstance(self.faulty_devices, str):
            self.faulty_devices = [self.faulty_devices]
        task = LocalizationSubmission(faulty_devices=self.faulty_devices)
        return task


if __name__ == "__main__":
    task = LocalizationSubmission(faulty_devices=["router_1", "switch_2"])
    print(task.model_json_schema())

    print(task)
