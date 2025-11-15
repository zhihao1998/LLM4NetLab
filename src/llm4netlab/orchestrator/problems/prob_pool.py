# import importlib
# import inspect

# import pkgutil
# from collections import defaultdict
from typing import Dict, Type

from llm4netlab.orchestrator.problems.device_failure.frr_failure import (
    FrrDownDetection,
    FrrDownLocalization,
    FrrDownRCA,
)
from llm4netlab.orchestrator.problems.problem_base import RootCauseCategory, TaskLevel
from llm4netlab.orchestrator.tasks.base import TaskBase

# def _register_problems():
#     """Register all available problems in the pool."""

#     problems = defaultdict(dict)
#     package = importlib.import_module("llm4netlab.orchestrator.problems")

#     for root_cause_category_info in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + "."):
#         if root_cause_category_info.name.count(".") == package.__name__.count(".") + 1:
#             continue  # Skip same level packages

#         root_cause_category_name = root_cause_category_info.name
#         root_cause_category_module = importlib.import_module(root_cause_category_name)

#         for issue_name, issue_obj in inspect.getmembers(root_cause_category_module, inspect.isclass):
#             if issue_obj.__module__ == root_cause_category_module.__name__:
#                 if "base" in issue_name.lower():
#                     continue
#                 problem_class: Type[TaskBase] = issue_obj
#                 root_cause_type = problem_class.META.id
#                 task_level = problem_class.META.task_level
#                 problems[root_cause_type][task_level] = problem_class
#     return problems


# _PROBLEMS: Dict[str, Type[TaskBase]] = _register_problems()

_PROBLEMS: Dict[str, Type[TaskBase]] = {
    FrrDownDetection.META.root_cause_type: {
        FrrDownDetection.META.task_level: FrrDownDetection,
        FrrDownLocalization.META.task_level: FrrDownLocalization,
        FrrDownRCA.META.task_level: FrrDownRCA,
    }
}


def get_submission_template(root_cause_type: str, task_level: TaskLevel) -> str:
    """Get the submission instruction for a specific problem.

    Args:
        root_cause_type: The root cause type.
        task_level: The task level.

    Returns:
        str: The submission instruction.
    """
    if root_cause_type in _PROBLEMS:
        if task_level in _PROBLEMS[root_cause_type]:
            return _PROBLEMS[root_cause_type][task_level].SUBMISSION.model_json_schema()
    raise ValueError(f"Problem {root_cause_type} - {task_level} not found.")


def list_avail_root_cause_categories() -> list[str]:
    """List available root cause categories.
    Returns:
        list[str]: List of available root cause categories.
    """
    return [category.value for category in RootCauseCategory]


def list_avail_root_cause_types(root_cause_category: str) -> list[str]:
    """List available root cause types for a specific root cause category.
    Args:
        root_cause_category (str): The root cause category.
    Returns:
        list[str]: List of available root cause types.
    """
    avail_types = []

    for prob_type, prob_cls_dict in _PROBLEMS.items():
        for _, prob_cls in prob_cls_dict.items():
            if prob_cls.META.root_cause_category.value == root_cause_category:
                avail_types.append(prob_type)
                break
    return avail_types


def get_problem_instance(root_cause_type: str, task_level: TaskLevel) -> TaskBase:
    """Get the problem instance for a specific root cause type and task level.
    Args:
        root_cause_type (str): The root cause type of the problem.
        task_level (TaskLevel): The task level of the problem.
    Returns:
        TaskBase: The problem instance.
    """
    try:
        return _PROBLEMS[root_cause_type][task_level]()
    except KeyError:
        raise ValueError(f"Problem with root cause type {root_cause_type} and task level {task_level} not found.")


if __name__ == "__main__":
    # print(list_avail_problems("host_ip_missing_detection"))
    for prob_id, prob_cls in _PROBLEMS.items():
        for level, cls in prob_cls.items():
            print(f"Problem ID: {prob_id}, Task Level: {level}, Class: {cls.__name__}")

    print(get_submission_template(FrrDownDetection.META.root_cause_type, TaskLevel.RCA))

    print(list_avail_root_cause_categories())
    print(list_avail_root_cause_types(FrrDownDetection.META.root_cause_category.value))
