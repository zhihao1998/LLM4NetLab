"""Define and query information about an Detection task."""

from pydantic import BaseModel, Field

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase


# TODO: should be the final outcome of the mitigation, like full connectivity restored, or minimum path
class MitigationSubmission(BaseModel):
    issue_type: str = Field(
        description="Type of issue being mitigated. Must be selected from known available issue types."
    )
    problem_id: str = Field(
        description="Problem identifier being mitigated. Must be selected from known available problem ids."
    )
    target_component_id: str = Field(
        description="The identifier of the target component to mitigate (e.g., device name, interface, link)."
    )
    mitigation_action: str = Field(
        description="Description of the action or approach proposed to mitigate the problem."
    )


class MitigationTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.net_env = net_env
        self.lab_name = net_env.name
        self.net_summary = self.net_env.net_summary()

        self.task_desc = """\
            The network you are working with is described below:
            {net_summary}

            You will propose a mitigation for a previously detected and localized anomaly.
            Based on the identified issue_type, problem_id, and target component(s),
            describe how to mitigate or resolve the issue.

            Focus only on verifying whether the proposed mitigation addresses the issue.

            Once ready, call the appropriate submission tool and submit your solutions.
            """
