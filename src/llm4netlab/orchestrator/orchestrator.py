import logging
import os
import time

from llm4netlab.config import BASE_DIR
from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance
from llm4netlab.utils.errors import SessionPrint
from llm4netlab.utils.session import Session

"""Orchestrator class that interfaces with the agent and the environment."""


class Orchestrator:
    def __init__(self):
        self.agent = None
        self.session = None
        self.session_print = SessionPrint()
        self.problem = None

        self.orchestration_start_time = None
        self.orchestration_end_time = None
        self.logger = logging.getLogger(__name__)

    def init_problem(self, problem_id: str) -> tuple:
        """Initialize the problem to solve.

        Args:
            problem_id: The problem ID.

        Returns:
            str: The task description.
            str: The session ID.
            str: The problem ID.
            str: The lab name.
        """
        self.orchestration_start_time = time.time()

        self.session = Session()
        self.logger.info(f"Initialized ID: {self.session.session_id}")

        self.problem_id = problem_id
        self.problem = get_problem_instance(problem_id)
        self.session.set_problem(self.problem, problem_id)
        # self.session.set_agent(self.agent_name)

        # deploy the network environment
        # check if the environment is already deployed
        if not self.problem.net_env.lab_exists():
            self.problem.net_env.deploy()
            self.logger.info(f"Deployed network environment {self.problem.net_env.name}.")
        else:
            self.logger.info(f"Network environment {self.problem.net_env.name} already deployed. Skipping deployment.")

        self.problem.inject_fault()

        # Get the problem description, instructions, and APIs
        task_desc = self.problem.get_task_description()

        os.makedirs(f"{BASE_DIR}/results/{self.problem_id}", exist_ok=True)
        # Log the problem and descriptions as ground truth
        with open(f"{BASE_DIR}/results/{self.problem_id}/{self.session.session_id}_groundtruth.log", "a+") as log_file:
            log_file.write(self.problem.SUBMISSION.model_dump_json() + "\n")
        return task_desc, self.session.session_id, self.problem_id, self.problem.net_env.name

    def register_agent(self, agent, agent_name) -> None:
        """Register an agent with the orchestrator.

        Args:
            agent: The agent to register.
            agent_name: The name of the agent.
        """
        self.agent = agent
        self.agent_name = agent_name

    def stop_problem(self, cleanup=False):
        """Stop the problem."""
        assert self.session is not None, "Session not initialized"
        assert self.problem is not None, "Problem not initialized"

        self.orchestration_end_time = time.time()
        if cleanup:
            self.problem.net_env.undeploy()
            self.logger.info(f"Undeployed network environment {self.problem.net_env.name}.")
