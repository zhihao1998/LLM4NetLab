"""Define and query information about an Detection task."""

import textwrap

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.actions.discovery import DiscoveryActions
from llm4netlab.orchestrator.tasks.base import TaskBase
from llm4netlab.utils.actions import get_actions
from llm4netlab.utils.errors import InvalidActionError


class DiscoveryTask(TaskBase):
    def __init__(self, net_env: NetworkEnvBase):
        super().__init__()
        self.actions = DiscoveryActions()
        self.net_env = net_env
        self.net_env_name = net_env.name
        self.net_summary = self.net_env.net_summary()

        self.task_desc = """\
            You are an expert networking engineer who has been tasked with detecting anomalies in a deployed network topology.

            The network you are working with today is described below:
            {net_summary}

            You will begin by analyzing the network's topology, connectivity and reachability, and then submit your findings:
            1. str: How the network is connected?
            2. str: The actual reachability of all devices in the network.
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
        return get_actions(task="discovery")

    def perform_action(self, action_name, *args, **kwargs):
        action_method = getattr(self.actions, action_name, None)

        if action_method is not None and callable(action_method):
            return action_method(*args, **kwargs)
        else:
            raise InvalidActionError(action_name)
