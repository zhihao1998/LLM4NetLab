"""Define and query information about an Detection task."""

from pydantic import BaseModel, Field

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase


class LocalizationSubmission(BaseModel):
    issue_type: str = Field(description="Type of issue detected. Must be selected from known available issue types.")
    problem_id: str = Field(description="Type of problem detected. Must be selected from known available problem ids.")
    target_component_ids: list[str] = Field(
        default_factory=list,
        description="List of IDs of components identified as the source of the problem. e.g., ['router_1', 'eth0']",
    )


class LocalizationTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase, fault_desc: str = ""):
        super().__init__()
        self.net_env = net_env
        self.lab_name = net_env.name
        self.get_info = self.net_env.get_info()
        self.fault_desc = fault_desc  # Note: here we add the fault description to tell the agent what to localize, instead of asking it to figure it out from scratch

        self.task_desc = """\
            The network you are working with is described below:
            {get_info}

            You will begin by localizing the anomalies.
            Pinpoint the faulty component(s), such as device, interface, link, prefix, neighbor, or path segment.
            Do not analyze root causes or propose mitigations.
            Once identified, call the appropriate submission tool and submit your findings.
            Do not end the session until you have submitted your solution through the API.
            """
