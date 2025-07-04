"""Define and query information about an Detection task."""

import textwrap

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.actions.detection import DetectionActions
from llm4netlab.orchestrator.tasks.base import TaskBase
from llm4netlab.utils.actions import get_actions
from llm4netlab.utils.errors import InvalidActionError


class DetectionTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.actions = DetectionActions()
        self.net_env = net_env
        self.net_env_name = net_env.name
        self.net_summary = self.net_env.net_summary()

        self.task_desc = """\
            You are an expert networking engineer who has been tasked with detecting anomalies in a deployed network topology. Please be very precise in your analysis and provide detailed evidence about any anomalies you detect.

            The network you are working with today is described below:
            {net_summary}

            You will begin by analyzing the network's state, detect anomalies, locate the root cause, and then submit your solution:
            1. str: `Yes` or `No` to indicate whether there are anomalies detected
            2. str: If `Yes`, locate the specific switch and port where the anomaly is detected, e.g., `s1:port1`
            3. str: If `Yes`, provide a description of the anomaly detected, e.g., `Packet loss detected on port 1`
            """

        self.instructions = """\
            You will respond with one of the above APIs as your next action.
            Please respond in the following format in a markdown code block:
            ```
            <API_NAME>(<API_PARAM1>, <API_PARAM2> ...)
            ```

            For example:
            ```
            get_reachability("NET_ENV_NAME")      # Get the reachability of the network env NET_ENV_NAME
            ```

            Please respond with only a single action per turn.
            """

    def get_task_description(self):
        return textwrap.dedent(self.task_desc).format(net_summary=self.net_summary)

    def get_instructions(self):
        return textwrap.dedent(self.instructions)

    def get_available_actions(self):
        return get_actions(task="detection")

    def perform_action(self, action_name, *args, **kwargs):
        action_method = getattr(self.actions, action_name, None)

        if action_method is not None and callable(action_method):
            return action_method(*args, **kwargs)
        else:
            raise InvalidActionError(action_name)
