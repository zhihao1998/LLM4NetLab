"""Define and query information about an Detection task."""

import textwrap
from typing import Any

from ai4netops.orchestrator.tasks.base import Task


class DetectionTask(Task):
    def __init__(self):
        super().__init__()
        self.actions = DetectionActions()

        self.task_desc = """\
            You are an expert DevOps engineer who has been tasked with detecting anomalies in a deployed service.

            The service you are working with today is described below:
            {app_summary}

            You will begin by analyzing the service's state and telemetry, and then submit your solution:
            1. str: `Yes` or `No` to indicate whether there are anomalies detected
            """

        self.instructions = """\
            You will respond with one of the above APIs as your next action.
            Please respond in the following format in a markdown code block:
            ```
            <API_NAME>(<API_PARAM1>, <API_PARAM2> ...)
            ```

            For example:
            ```
            exec_shell("ls -l")      # will list files in current directory
            ```

            Please respond with only a single action per turn.
            """

    def get_task_description(self):
        return textwrap.dedent(self.task_desc).format(app_summary=self.app_summary)

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

    def eval(self, soln: Any, trace: list[SessionItem], duration: float):
        self.add_result("TTD", duration)
        self.common_eval(trace)
        return self.results
