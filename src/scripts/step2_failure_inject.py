import json
import logging
import random

from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance, list_avail_problem_names
from llm4netlab.orchestrator.problems.problem_base import TaskLevel
from llm4netlab.utils.logger import system_logger
from llm4netlab.utils.session import Session


def inject_failure(problem_names: list[str], re_inject: bool = True):
    """
    Inject failure into the network environment based on the root cause name.
    """
    logger = system_logger

    session = Session()
    session.load_running_session()
    # save session data for follow-up steps
    session.update_session("problem_names", problem_names)

    for problem_name in problem_names:
        # check if problem_name in the available problems
        if problem_name not in list_avail_problem_names():
            raise ValueError(f"Unknown problem name: {problem_name}")

    scenario_params = session.scenario_params if hasattr(session, "scenario_params") else {}

    tot_tasks = []
    for task_level in TaskLevel:
        random.seed(session.session_id[-4:])
        problem = get_problem_instance(
            problem_names=problem_names, task_level=task_level, scenario_name=session.scenario_name, **scenario_params
        )
        tot_tasks.append(problem)

    if re_inject:
        tot_tasks[0].inject_fault()

    logger.info(f"Session {session.session_id}, injected problem(s): {problem_names} under {session.scenario_name}.")
    task_description = problem.get_task_description()

    session.update_session("task_description", task_description)

    # save the ground truth for evaluation
    tot_gt = {}
    for problem in tot_tasks:
        gt = problem.get_submission().model_dump_json()
        tot_gt.update(json.loads(gt))

    session.write_gt(tot_gt)
    logger.info(f"Ground truth saved for session ID: {session.session_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    inject_failure(["frr_service_down"], True)
