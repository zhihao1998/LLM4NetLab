import textwrap

from pydantic import BaseModel

from llm4netlab.net_env.base import NetworkEnvBase


class TaskBase:
    """Base class for all tasks."""

    META: BaseModel = None
    SUBMISSION: BaseModel = None

    def __init__(self):
        self.results = {}
        self.net_env: NetworkEnvBase = None

    def inject_fault(self):
        return NotImplementedError("")

    def get_instructions(self):
        raise NotImplementedError()

    def add_result(self, key, value):
        """Add an evaluation result to the task."""
        self.results[key] = value

    def get_task_description(self):
        return textwrap.dedent(self.task_desc).format(net_summary=self.net_summary)
