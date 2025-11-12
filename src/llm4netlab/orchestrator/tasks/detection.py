"""Define and query information about an Detection task."""

from pydantic import BaseModel, Field

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase


class DetectionSubmission(BaseModel):
    is_anomaly: bool = Field(description="Indicates whether an anomaly was detected.")


class DetectionTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.net_env = net_env
        self.lab_name = net_env.name
        self.get_info = self.net_env.get_info()

        self.task_desc = """\
            The network you are working with is described below:
            {get_info}

            You will begin by analyzing the network's state, and detect anomalies.
            Indicate whether there is an anomaly in the network. No need for further analysis or mitigation.
            Once finished, call the appropriate submission tool and submit your findings.
            Do not end the session until you have submitted your solution through the API.
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
        if is_anomaly in ["True", "true", "1", 1, True]:
            is_anomaly = True
        elif is_anomaly in ["False", "false", "0", 0, False]:
            is_anomaly = False
        else:
            return 0.0
        if is_anomaly == self.META.is_anomaly:
            return 1.0
        return 0.0
