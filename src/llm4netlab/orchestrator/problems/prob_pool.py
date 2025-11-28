import importlib
import inspect
import logging
import pkgutil
from collections import defaultdict
from typing import Dict, Type

from llm4netlab.orchestrator.problems.multi_problems import MultiFaultDetection, MultiFaultLocalization, MultiFaultRCA
from llm4netlab.orchestrator.problems.problem_base import TaskLevel
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
                root_cause_name = problem_class.META.root_cause_name
                task_level = problem_class.META.task_level
                if root_cause_name not in problems:
                    problems[root_cause_name] = {}
                problems[root_cause_name][task_level] = problem_class
            except Exception as e:
                logger.warning(f"Failed to register class {cls_name} in {root_cause_category_name}: {e}")
                continue
    return problems


_PROBLEMS: Dict[str, Type[TaskBase]] = _register_problems()


def list_avail_problem_names() -> list[str]:
    """List all available root cause names."""
    return list(_PROBLEMS.keys())


def list_avail_problem_instances() -> list[Type[TaskBase]]:
    return _PROBLEMS


def list_avail_tags() -> list[str]:
    """List all available tags for problems."""
    tags = set()
    for problem_classes in _PROBLEMS.values():
        for problem_class in problem_classes.values():
            tags.update(problem_class.TAGS)
    return list(tags)


def get_problem_instance(problem_names: list, task_level: TaskLevel, scenario_name: str, **kwargs) -> TaskBase:
    """Get the problem instance for a specific root cause name and task level.
    Args:
        problem_names (list): The root cause names of the problem.
    Returns:
        TaskBase: The problem instance.
    """
    if not isinstance(problem_names, list) or len(problem_names) == 0:
        raise ValueError("problem_names should be a list of problem_names.")

    # Multi-fault scenario
    if len(problem_names) > 1:
        match task_level:
            case TaskLevel.DETECTION:
                return MultiFaultDetection(
                    sub_faults=[
                        _PROBLEMS[fault_name][task_level](scenario_name=scenario_name, **kwargs)
                        for fault_name in problem_names
                    ],
                    scenario_name=scenario_name,
                    **kwargs,
                )
            case TaskLevel.LOCALIZATION:
                return MultiFaultLocalization(
                    sub_faults=[
                        _PROBLEMS[fault_name][task_level](scenario_name=scenario_name, **kwargs)
                        for fault_name in problem_names
                    ],
                    scenario_name=scenario_name,
                    **kwargs,
                )
            case TaskLevel.RCA:
                return MultiFaultRCA(
                    sub_faults=[
                        _PROBLEMS[fault_name][task_level](scenario_name=scenario_name, **kwargs)
                        for fault_name in problem_names
                    ],
                    scenario_name=scenario_name,
                    **kwargs,
                )
            case _:
                raise ValueError(f"Unsupported task level for multi-fault: {task_level}")

    # Single-fault scenario
    else:
        return _PROBLEMS[problem_names[0]][task_level](scenario_name=scenario_name, **kwargs)


if __name__ == "__main__":
    problems = list_avail_problem_names()

    print(problems)
