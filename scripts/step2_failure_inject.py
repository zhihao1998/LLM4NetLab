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
    session.update_session("problem_names", problem_names)
    session.update_session("task_level", task_level.value)

    for problem_name in problem_names:
        # check if problem_name in the available problems
        if problem_name not in list_avail_problems():
            raise ValueError(f"Unknown problem name: {problem_name}")

    net_env_params = session.net_env_params if hasattr(session, "net_env_params") else {}
    problem = get_problem_instance(
        problem_names=problem_names, task_level=task_level, net_env_name=session.net_env_name, **net_env_params
    )
    problem.inject_fault()
    logger.info(
        f"Session {session.session_id}, injected problem(s): {problem_names} at task level {task_level.value} under {session.net_env_name}."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Inject Failure into Network Environment")
    parser.add_argument(
        "problem_names",
        type=str,
        nargs="*",
        default=["link_down", "host_missing_ip"],
        help="Name(s) of the problem(s) to inject, space-separated if multiple (default: link_failure)",
    )
    parser.add_argument(
        "task_level",
        type=str,
        nargs="?",
        choices=[level.value for level in TaskLevel],
        default=TaskLevel.DETECTION,
        help="Task level for the problem (default: detection)",
    )
    args = parser.parse_args()

    problem_names = [name.strip() for name in args.problem_names]
    task_level = TaskLevel(args.task_level)
    inject_failure(problem_names, task_level)
