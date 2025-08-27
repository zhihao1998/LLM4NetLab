"""Define and query information about an Detection task."""

import textwrap

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase


class DetectionTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.net_env = net_env
        self.lab_name = net_env.name
        self.net_summary = self.net_env.net_summary()

        self.task_desc = """\
            The network you are working with today is described below:
            {net_summary}

            You will begin by analyzing the network's state, detect anomalies, then report your solution:
            1. str: `Yes` or `No` to indicate whether there are anomalies detected.
            """

    def get_task_description(self):
        return textwrap.dedent(self.task_desc).format(net_summary=self.net_summary)
