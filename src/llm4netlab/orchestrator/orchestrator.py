import json
import logging
import os
import time

from llm4netlab.config import BASE_DIR, RESULTS_DIR
from llm4netlab.evaluator.llm_judge import LLMJudge
from llm4netlab.evaluator.result_log import EvalResult, record_eval_result
from llm4netlab.evaluator.trace_parser import AgentTraceParser
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

        # get the network environment information
        # net_env_info = self.problem.net_env.get_info()

        os.makedirs(f"{BASE_DIR}/results/{self.problem_id}", exist_ok=True)
        # Log the problem and descriptions as ground truth
        with open(f"{BASE_DIR}/results/{self.problem_id}/{self.session.session_id}_groundtruth.log", "a+") as log_file:
            log_file.write(self.problem.SUBMISSION.model_dump_json() + "\n")
        return task_desc, self.session.session_id, self.problem_id, self.problem.net_env.name

    def register_agent(self, agent) -> None:
        """Register an agent with the orchestrator.

        Args:
            agent: The agent to register.
        """
        self.agent = agent
        self.agent_name = agent.agent_name
        self.backend_model = agent.backend_model

    def stop_problem(self, cleanup=False):
        """Stop the problem."""
        assert self.session is not None, "Session not initialized"
        assert self.problem is not None, "Problem not initialized"

        self.orchestration_end_time = time.time()
        if cleanup:
            self.problem.net_env.undeploy()
            self.logger.info(f"Undeployed network environment {self.problem.net_env.name}.")

    def eval(self):
        # Check if there is valid submission
        sub_log_path = f"{RESULTS_DIR}/{self.problem_id}/{self.session.session_id}_{self.backend_model}_submission.log"
        if not os.path.exists(sub_log_path):
            evaluator_score = -1
        else:
            with open(sub_log_path, "r") as f:
                submission = json.load(f)
            # task-specific evaluation
            evaluator_score = self.problem.eval(submission=submission)

        # agent trace
        trace_path = os.path.join(
            RESULTS_DIR, self.problem_id, f"{self.session.session_id}_{self.backend_model}_conversation.log"
        )

        # llm as judge evaluation
        llm_judge = LLMJudge()
        _, llm_score = llm_judge.evaluate_agent(
            problem_description=self.problem.META.description,
            net_env_info=self.problem.net_env.get_info(),
            trace_path=trace_path,
            save_path=f"{RESULTS_DIR}/{self.problem_id}/{self.session.session_id}_{self.backend_model}_llm_judge.log",
        )

        # parse agent trace
        trace_parser = AgentTraceParser(trace_path=trace_path)
        trace_metrics = trace_parser.parse_trace()

        # log evaluation results
        eval_result = EvalResult()
        eval_result.agent_name = self.agent_name
        eval_result.model_name = self.backend_model
        eval_result.problem_id = self.problem_id
        eval_result.net_env = self.problem.net_env.name
        eval_result.session_id = self.session.session_id
        eval_result.in_tokens = trace_metrics["in_tokens"]
        eval_result.out_tokens = trace_metrics["out_tokens"]
        eval_result.steps = trace_metrics["steps"]
        eval_result.tool_calls = trace_metrics["tool_calls"]
        eval_result.tool_errors = trace_metrics["tool_errors"]
        eval_result.time_taken = trace_metrics["time_taken"]
        eval_result.llm_judge_score = llm_score
        eval_result.evaluator_score = evaluator_score

        record_eval_result(eval_result)
