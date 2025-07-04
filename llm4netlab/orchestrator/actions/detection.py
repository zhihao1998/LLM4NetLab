from typing import List

from llm4netlab.orchestrator.actions.base import AcionBase
from llm4netlab.utils.actions import action
from llm4netlab.utils.submission import SubmissionStatus


class DetectionActions(AcionBase):
    """Discovery actions for the network."""

    @staticmethod
    @action
    def submit(discovery_result: List[str]) -> SubmissionStatus:
        """Submit the discovery result to the orchestrator.

        Args:
            discovery_result (List[str]): The discovery result.

        Returns:
            str: The response from the orchestrator.
        """
        return SubmissionStatus.VALID_SUBMISSION
