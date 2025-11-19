from pydantic import BaseModel

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta


class TaskBase:
    """Base class for all tasks."""

    ROOT_CAUSE_CATEGORY: str = None
    ROOT_CAUSE_NAME: str = None

    META: ProblemMeta = None
    SUBMISSION: BaseModel = None

    def __init__(self):
        self.results = {}
        self.net_env: NetworkEnvBase = None

    def inject_fault(self):
        return NotImplementedError()

    def get_instructions(self):
        raise NotImplementedError()

    def add_result(self, key, value):
        """Add an evaluation result to the task."""
        self.results[key] = value

    def get_task_description(self) -> str:
        """Get the task description with network and symptom details.

        Returns:
            str: The formatted task description.
        """
        return self.task_desc()

    def eval(self, submission: dict) -> float:
        """Task-specific evaluation
        Args:
            submission: The submission to evaluate.

        Returns:
            float: The evaluation score.
        """
        return NotImplementedError()
