import importlib
import inspect
import json
import logging
import pkgutil
from collections import defaultdict
from typing import Dict, Type

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.orchestrator.tasks.base import TaskBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _register_problems():
    """Register all available problems in the pool."""

    problems = defaultdict(dict)
    package = importlib.import_module("llm4netlab.orchestrator.problems")

    for info in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + "."):
        # Skip direct sub-packages
        if info.name.count(".") == package.__name__.count(".") + 1:
            continue

        root_cause_category_name = info.name

        # Safely import the module
        try:
            module = importlib.import_module(root_cause_category_name)
        except Exception as e:
            logger.warning(f"Failed to import {root_cause_category_name}: {e}")
            continue
        # Safely get classes from the module
        try:
            members = inspect.getmembers(module, inspect.isclass)
        except Exception as e:
            logger.warning(f"Failed to inspect members of {root_cause_category_name}: {e}")
            continue
        # Register each problem class
        for cls_name, cls_obj in members:
            if cls_obj.__module__ != module.__name__:
                continue

            if "base" in cls_name.lower():
                continue

            try:
                problem_class: Type[TaskBase] = cls_obj
                root_cause_category_name = problem_class.META.root_cause_category.value
                root_cause_name = problem_class.META.root_cause_name
                task_level = problem_class.META.task_level.value
                if root_cause_name not in problems[root_cause_category_name]:
                    problems[root_cause_category_name][root_cause_name] = {}
                problems[root_cause_category_name][root_cause_name][task_level] = problem_class
            except Exception as e:
                logger.warning(f"Failed to register class {cls_name} in {root_cause_category_name}: {e}")
                continue
    return problems


_PROBLEMS: Dict[str, Type[TaskBase]] = _register_problems()


def list_avail_root_causes() -> list[str]:
    """List all available root cause categories and their corresponding root cause names."""
    avail_causes = []

    for cause_category, cause_category_dict in _PROBLEMS.items():
        for cause_name in cause_category_dict.keys():
            avail_causes.append(
                json.dumps(
                    {
                        "root_cause_category": str(cause_category),
                        "root_cause_name": str(cause_name),
                    }
                )
            )
    return avail_causes


def get_problem_instance(root_cause_name: str, task_level: str, net_env: NetworkEnvBase) -> TaskBase:
    """Get the problem instance for a specific root cause name and task level.
    Args:
        root_cause_name (str): The root cause name of the problem.
        task_level (str): The task level of the problem.
    Returns:
        TaskBase: The problem instance.
    """
    res_instance = None
    for _, cause_category_dict in _PROBLEMS.items():
        for cause_name, cause_cls in cause_category_dict.items():
            if str(cause_name) == str(root_cause_name):
                for level, cls in cause_cls.items():
                    if str(level) == str(task_level):
                        res_instance = cls(net_env=net_env)
                        break
    return res_instance


if __name__ == "__main__":
    # for prob_id, prob_cls in _PROBLEMS.items():
    #     for level, cls in prob_cls.items():
    #         print(f"Problem ID: {prob_id}, Task Level: {level}, Class: {cls.__name__}")

    # print(get_submission_template(FrrDownDetection.META.root_cause_name, TaskLevel.RCA))

    problems = list_avail_root_causes()
    for prob in problems:
        print(prob)
    print(get_problem_instance("link_high_latency", "rca", None))
