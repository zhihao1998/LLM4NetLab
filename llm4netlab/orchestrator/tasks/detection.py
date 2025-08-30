"""Define and query information about an Detection task."""

import textwrap

from pydantic import BaseModel, Field

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase


class DetectionSubmission(BaseModel):
    is_anomaly: bool = Field(description="Indicates whether an anomaly was detected.")
    issue_type: str = Field(description="Type of issue detected. Must be selected from known available issue types.")
    problem_id: str = Field(description="Type of problem detected. Must be selected from known available problem ids.")


class DetectionTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.net_env = net_env
        self.lab_name = net_env.name
        self.net_summary = self.net_env.net_summary()

        self.task_desc = """\
            The network you are working with today is described below:
            {net_summary}

            You will begin by analyzing the network's state, and detect anomalies:
            1. Detection: Indicate whether there is an anomaly in the network. No need for further analysis or mitigation.
            Once finished, call the appropriate submission tool and submit your findings.
            """

    def get_task_description(self):
        return textwrap.dedent(self.task_desc).format(net_summary=self.net_summary)
