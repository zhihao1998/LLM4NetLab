import json
import logging
import os
import textwrap
import time

from llm4netlab.config import RESULTS_DIR
from llm4netlab.evaluator.llm_judge import LLMJudge
from llm4netlab.evaluator.result_log import EvalResult, record_eval_result
from llm4netlab.evaluator.trace_parser import AgentTraceParser
from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance
from llm4netlab.orchestrator.problems.problem_base import TaskLevel
from llm4netlab.utils.session import Session

"""Orchestrator class that interfaces with the agent and the environment."""


class Orchestrator:
    def __init__(self):
        self.session = None
        self.problem = None

        self.orchestration_start_time = None
        self.orchestration_end_time = None
        self.logger = logging.getLogger(__name__)

    def init_problem(
        self,
        root_cause_name: str,
        task_level: TaskLevel,
        agent_name: str = None,
        backend_model_name: str = None,
        session_id: str = None,
        if_inject: bool = True,
    ) -> tuple:
        """Initialize the problem to solve.

        Args:
            root_cause_name: The root cause type.
            task_level: The task level.

        Returns:
            A tuple containing the root cause category, task description, session ID, and lab name.
        """
        self.orchestration_start_time = time.time()

        self.session = Session(session_id=session_id)
        self.logger.info(f"Initialized ID: {self.session.session_id}")

        self.root_cause_name = root_cause_name
        self.task_level = task_level
        self.agent_name = agent_name
        self.backend_model = backend_model_name
        self.log_prefix = f"{self.session.session_id}_{self.backend_model}"

        self.problem = get_problem_instance(root_cause_name, task_level)
        self.session.set_problem(self.problem, root_cause_name)

        self.root_cause_category = self.problem.META.root_cause_category
        self.log_dir = f"{RESULTS_DIR}/{self.root_cause_category}/{self.root_cause_name}/{self.task_level}"
        os.makedirs(self.log_dir, exist_ok=True)

        # deploy the network environment
        # check if the environment is already deployed
        if not self.problem.net_env.lab_exists():
            self.problem.net_env.deploy()
            self.logger.info(f"Deployed network environment {self.problem.net_env.name}.")
        else:
            self.logger.info(f"Network environment {self.problem.net_env.name} already deployed. Skipping deployment.")

        if if_inject:
            self.problem.inject_fault()

        # Get the problem description, instructions, and APIs
        task_desc = self.problem.get_task_description()

        # Log the problem and descriptions as ground truth
        with open(f"{self.log_dir}/{self.session.session_id}_groundtruth.log", "w+") as log_file:
            log_file.write(self.problem.SUBMISSION.model_dump_json() + "\n")
        return self.root_cause_category, task_desc, self.session.session_id, self.problem.net_env.name

    def stop_problem(self, cleanup=False):
        """Stop the problem."""
        assert self.session is not None, "Session not initialized"
        assert self.problem is not None, "Problem not initialized"

        self.orchestration_end_time = time.time()
        if cleanup:
            self.problem.net_env.undeploy()
            self.logger.info(f"Undeployed network environment {self.problem.net_env.name}.")

    def eval_problem(self):
        """Evaluate the problem solution and log the results."""
        sub_log_path = f"{self.log_dir}/{self.log_prefix}_submission.log"
        if not os.path.exists(sub_log_path):
            evaluator_score = -1
        else:
            with open(sub_log_path, "r") as f:
                submission = json.load(f)
            # task-specific evaluation
            evaluator_score = round(self.problem.eval(submission=submission), 2)

        # agent trace
        trace_path = os.path.join(self.log_dir, f"{self.log_prefix}_conversation.log")

        self.logger.info(f"Evaluating session {self.session.session_id} using LLM-as-Judge.")
        # llm as judge evaluation
        llm_judge = LLMJudge()
        _, llm_score = llm_judge.evaluate_agent(
            problem_description=self.problem.META.description,
            net_env_info=self.problem.net_env.get_info(),
            ground_truth=textwrap.dedent(f"""\
                The root cause category is {self.problem.ROOT_CAUSE_CATEGORY}.
                The root cause name is {self.problem.ROOT_CAUSE_NAME}.
            """),
            trace_path=trace_path,
            save_path=f"{self.log_dir}/{self.log_prefix}_llm_judge.log",
        )

        # parse agent trace
        trace_parser = AgentTraceParser(trace_path=trace_path)
        trace_metrics = trace_parser.parse_trace()

        self.logger.info(f"All Done! LLM Judge Score: {llm_score}, Evaluator Score: {evaluator_score}")

        # log evaluation results
        eval_result = EvalResult(
            agent_name=self.agent_name,
            backend_model_name=self.backend_model,
            root_cause_category=self.root_cause_category,
            root_cause_name=self.root_cause_name,
            task_level=self.task_level,
            net_env=self.problem.net_env.name,
            session_id=self.session.session_id,
            in_tokens=trace_metrics.get("in_tokens", None),
            out_tokens=trace_metrics.get("out_tokens", None),
            steps=trace_metrics.get("steps", None),
            tool_calls=trace_metrics.get("tool_calls", None),
            tool_errors=trace_metrics.get("tool_errors", None),
            time_taken=self.orchestration_end_time - self.orchestration_start_time,
            llm_judge_score=llm_score,
            evaluator_score=evaluator_score,
        )

        record_eval_result(eval_result)
