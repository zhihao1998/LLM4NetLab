import textwrap

from pydantic import BaseModel

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.problems.problem_base import ProblemMeta


class TaskBase:
    """Base class for all tasks."""

    root_cause_category: str = None
    root_cause_name: str = None

    META: ProblemMeta = None

    def __init__(self):
        self.results = {}
        self.scenario_name: NetworkEnvBase = None

    def inject_fault(self):
        return NotImplementedError()

    def recover_fault(self):
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
        self.diagnostic_prompt = """\
            You are provided with the following network description and its current state:
            {net_desc}

            Your goal is to analyze the network condition and, if needed, use the available tools.
            You need to generate a troubeshooting diagnosis report.
            The report should reflect your assessment of the network's health, indicate any abnormal behavior you identify, and describe relevant findings based on your analysis.

            Focus on producing an informative and coherent diagnostic report derived from the network state.
            Do not need to propose any solutions or remediation steps at this stage.
            """

        tmpl = textwrap.dedent(self.diagnostic_prompt)
        text = tmpl.format(
            net_desc=self.net_env.get_info(),
        ).strip()
        return text

    def eval(self, submission: dict) -> float:
        """Task-specific evaluation
        Args:
            submission: The submission to evaluate.

        Returns:
            float: The evaluation score.
        """
        return NotImplementedError()

    def get_submission() -> BaseModel:
        """Get the submission model for the task.

        Returns:
            BaseModel: The submission model.
        """
        return NotImplementedError()
