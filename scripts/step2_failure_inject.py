import argparse
import logging

from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance, list_avail_problems
from llm4netlab.orchestrator.problems.problem_base import TaskLevel
from llm4netlab.utils.session import Session


def inject_failure(problem_names: list[str], task_level: TaskLevel):
    """
    Inject failure into the network environment based on the root cause name.
    """
    logger = logging.getLogger(__name__)

    session = Session()
    session.load_running_session()

    for problem_name in problem_names:
        # check if problem_name in the available problems
        if problem_name not in list_avail_problems():
            raise ValueError(f"Unknown problem name: {problem_name}")

    scenario_params = session.scenario_params if hasattr(session, "scenario_params") else {}
    problem = get_problem_instance(
        problem_names=problem_names, task_level=task_level, scenario_name=session.scenario_name, **scenario_params
    )
    problem.inject_fault()
    logger.info(
        f"Session {session.session_id}, injected problem(s): {problem_names} at task level {task_level.value} under {session.scenario_name}."
    )
    task_description = problem.get_task_description()

    # save session data for follow-up steps
    session.update_session("problem_names", problem_names)
    session.update_session("task_level", task_level.value)
    session.update_session("task_description", task_description)
    logger.info(f"Task description: {task_description}")

    # save the ground truth for evaluation
    gt = problem.get_submission().model_dump_json()
    session.write_gt(gt)
    logger.info(f"Ground truth saved for session ID: {session.session_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Inject Failure into Network Environment")
    parser.add_argument(
        "--problems",
        type=str,
        nargs="*",
        default=["link_down", "host_missing_ip"],
        help="Name(s) of the problem(s) to inject, space-separated if multiple (default: link_failure)",
    )
    parser.add_argument(
        "--task_level",
        type=str,
        nargs="?",
        choices=[level.value for level in TaskLevel],
        default=TaskLevel.RCA,
        help="Task level for the problem (default: detection)",
    )
    args = parser.parse_args()

    problem_names = [name.strip() for name in args.problems]
    task_level = TaskLevel(args.task_level)
    inject_failure(problem_names, task_level)
