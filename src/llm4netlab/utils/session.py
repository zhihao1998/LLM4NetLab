# This file includes code adapted from the following open-source project:
# https://github.com/microsoft/AIOpsLab
# Licensed under the MIT License.

# Original notice:
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Session wrapper to manage the an agent's session with the orchestrator."""

import datetime
import time

from pydantic import BaseModel

from llm4netlab.orchestrator.tasks.base import TaskBase


def generate_code():
    time_str = datetime.datetime.now().strftime("%m%d%H%M%S")
    return time_str


class SessionKey(BaseModel):
    lab_name: str
    session_id: str
    root_cause_category: str
    root_cause_name: str
    task_level: str
    backend_model_name: str
    agent_name: str


class Session:
    def __init__(self) -> None:
        # self.session_id = str(uuid.uuid4()).replace("-", "")
        self.session_id = generate_code()
        self.root_cause_name = None
        self.problem: TaskBase = None
        self.solution = None
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.agent_name = None

    def set_problem(self, problem: TaskBase, root_cause_name: str):
        """Set the problem instance for the session.

        Args:
            problem (TaskBase): The problem instance to set.
            root_cause_name (str): The root cause type.
        """
        self.problem = problem
        self.root_cause_name = root_cause_name

    def set_solution(self, solution):
        """Set the solution shared by the agent.

        Args:
            solution (Any): The solution instance to set.
        """
        self.solution = solution

    def set_results(self, results):
        """Set the results of the session.

        Args:
            results (Any): The results of the session.
        """
        self.results = results

    def set_agent(self, agent_name):
        """Set the agent name for the session.

        Args:
            agent_name (str): The name of the agent.
        """
        self.agent_name = agent_name

    def start(self):
        """Start the session."""
        self.start_time = time.time()

    def end(self):
        """End the session."""
        self.end_time = time.time()

    def get_duration(self) -> float:
        """Get the duration of the session."""
        duration = self.end_time - self.start_time
        return duration
