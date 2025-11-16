# import importlib
# import inspect

# import pkgutil
# from collections import defaultdict
import json
from typing import Dict, Type

from llm4netlab.orchestrator.problems.device_failure.frr_failure import (
    FrrDownDetection,
    FrrDownLocalization,
    FrrDownRCA,
)
from llm4netlab.orchestrator.problems.performance_degradation.web_issue import (
    DNSLookupLatencyDetection,
    DNSLookupLatencyLocalization,
    DNSLookupLatencyRCA,
)
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
#                 root_cause_name = problem_class.META.id
#                 task_level = problem_class.META.task_level
#                 problems[root_cause_name][task_level] = problem_class
#     return problems


# _PROBLEMS: Dict[str, Type[TaskBase]] = _register_problems()

_PROBLEMS: Dict[str, Type[TaskBase]] = {
    FrrDownDetection.META.root_cause_category: {
        FrrDownDetection.META.root_cause_name: {
            FrrDownDetection.META.task_level: FrrDownDetection,
            FrrDownLocalization.META.task_level: FrrDownLocalization,
            FrrDownRCA.META.task_level: FrrDownRCA,
        }
    },
    DNSLookupLatencyDetection.META.root_cause_category: {
        DNSLookupLatencyDetection.META.root_cause_name: {
            DNSLookupLatencyDetection.META.task_level: DNSLookupLatencyDetection,
            DNSLookupLatencyLocalization.META.task_level: DNSLookupLatencyLocalization,
            DNSLookupLatencyRCA.META.task_level: DNSLookupLatencyRCA,
        }
    },
}


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


def get_problem_instance(root_cause_name: str, task_level: str) -> TaskBase:
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
                        res_instance = cls()
                        break
    return res_instance


if __name__ == "__main__":
    # for prob_id, prob_cls in _PROBLEMS.items():
    #     for level, cls in prob_cls.items():
    #         print(f"Problem ID: {prob_id}, Task Level: {level}, Class: {cls.__name__}")

    # print(get_submission_template(FrrDownDetection.META.root_cause_name, TaskLevel.RCA))

    # print(list_avail_root_causes())
    print(get_problem_instance("frr_service_down", "rca"))
