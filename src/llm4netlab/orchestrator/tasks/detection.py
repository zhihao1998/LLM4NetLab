"""Define and query information about an Detection task."""

from pydantic import BaseModel, Field

from llm4netlab.orchestrator.tasks.base import TaskBase


class DetectionSubmission(BaseModel):
    is_anomaly: bool = Field(description="Indicates whether an anomaly was detected.")


class DetectionTask(TaskBase):
    def __init__(self):
        super().__init__()
        # Description of the symptoms observed in the network

        self.task_desc = """\
            The network you are working with is described below:
            {net_desc}

            Your task is to analyze the current network state and detect anomalies.
            Indicate whether there is an anomaly in the network (True/False).
            No need for further analysis, localization or mitigation.
            Once you have determined whether there is an anomaly, provide your conclusion for submission.
            """

    def eval(self, submission: dict) -> float:
        """Evaluate the detection task submission.

        Args:
            submission: The submission to evaluate.

        Returns:
            float: The evaluation score.
        """
        # If there is no is_anomaly field, return -1 score
        is_anomaly = submission.get("is_anomaly", -1.0)
        if is_anomaly in ["True", "true", "1", 1, True, "yes", "Yes"]:
            is_anomaly = True
        elif is_anomaly in ["False", "false", "0", 0, False, "no", "No"]:
            is_anomaly = False
        else:
            return 0.0
        if is_anomaly == self.SUBMISSION.is_anomaly:
            return 1.0
        return 0.0
