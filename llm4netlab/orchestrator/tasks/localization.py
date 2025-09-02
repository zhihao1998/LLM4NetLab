"""Define and query information about an Detection task."""

from pydantic import BaseModel, Field

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase


class LocalizationSubmission:
    class DeviceFailure(BaseModel):
        issue_type: str = Field(
            description="Type of issue detected. Must be selected from known available issue types."
        )
        problem_id: str = Field(
            description="Type of problem detected. Must be selected from known available problem ids."
        )
        failed_device: str = Field(description="Name of the failed device.")


class LocalizationTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.net_env = net_env
        self.lab_name = net_env.name
        self.net_summary = self.net_env.net_summary()

        self.task_desc = """\
            The network you are working with is described below:
            {net_summary}

            You will begin by analyzing the network's state, and localize anomalies. 
            If an anomaly exists, identify and specify its location in the network. 
            Pinpoint the faulty component(s), such as device, interface, link, prefix, neighbor, or path segment. 
            Do not analyze root causes or propose mitigations.
            Once identified, call the appropriate submission tool and submit your findings.
            """
