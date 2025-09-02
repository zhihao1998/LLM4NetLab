import json
from typing import Dict, Type

from pydantic import BaseModel

from llm4netlab.orchestrator.problems.config_access_policy_error.bgp_error import BgpAclBlockDetection
from llm4netlab.orchestrator.problems.config_access_policy_error.ospf_error import OspfAclBlockDetection
from llm4netlab.orchestrator.problems.config_routing_policy_error.bgp_error import BgpAsnMisconfigDetection
from llm4netlab.orchestrator.problems.config_routing_policy_error.ospf_error import OspfMisconfigDetection
from llm4netlab.orchestrator.problems.connectivity_loss.p4_packet_loss import P4PacketLossDetection
from llm4netlab.orchestrator.problems.device_failure.bmv2_failure import Bmv2DownDetection
from llm4netlab.orchestrator.problems.device_failure.frr_failure import FrrDownDetection, FrrDownLocalization
from llm4netlab.orchestrator.problems.p4_runtime_error.p4_tbl_entry_missing import P4TableEntryMissingDetection
from llm4netlab.orchestrator.problems.performance_degradation.p4_int import P4IntHopDelayHighDetection
from llm4netlab.orchestrator.tasks.base import TaskBase

_PROBLEMS: Dict[str, Type[TaskBase]] = {
    ####################
    #  Generic device failure issues
    ####################
    FrrDownDetection.META.id: FrrDownDetection,
    FrrDownLocalization.META.id: FrrDownLocalization,
    Bmv2DownDetection.META.id: Bmv2DownDetection,
    ####################
    #  BGP issues
    ####################
    # ref: https://support.huawei.com/enterprise/en/doc/EDOC1000177634/31f2a647/case-study-a-bgp-peer-relationship-fails-to-be-established#EN-US_CONCEPT_0000001180501803
    # An ACL filters out the packets carrying TCP port 179.
    BgpAclBlockDetection.META.id: BgpAclBlockDetection,
    # ASN misconfiguration can cause BGP peer relationship to fail.
    BgpAsnMisconfigDetection.META.id: BgpAsnMisconfigDetection,
    ####################
    #  OSPF issues
    ####################
    OspfAclBlockDetection.META.id: OspfAclBlockDetection,
    OspfMisconfigDetection.META.id: OspfMisconfigDetection,
    ####################
    #  P4 issues
    ####################
    P4TableEntryMissingDetection.META.id: P4TableEntryMissingDetection,
    ####################
    #  INT issues
    ####################
    P4IntHopDelayHighDetection.META.id: P4IntHopDelayHighDetection,
    ####################
    #  Generic issues
    ####################
    P4PacketLossDetection.META.id: P4PacketLossDetection,
}


def get_submit_instruction(problem_id: str) -> str:
    """Get the submission instruction for a specific problem.

    Args:
        problem_id: The problem ID.

    Returns:
        str: The submission instruction.
    """
    if problem_id in _PROBLEMS:
        return _PROBLEMS[problem_id].get_submit_instruction()
    else:
        raise ValueError(f"Problem ID {problem_id} not found in the pool.")


def list_avail_problems(problem_id: str) -> list[str]:
    """To provide the agent choices for solution submission."""
    if problem_id not in _PROBLEMS:
        raise ValueError(f"Problem ID {problem_id} not found in the pool.")

    all_avail_problems = []

    for prob in _PROBLEMS.values():
        if prob.META.problem_level == _PROBLEMS[problem_id].META.problem_level:
            all_avail_problems.append(
                json.dumps(
                    {
                        "id": prob.META.id,
                        "description": prob.META.description,
                        "issue_type": prob.META.issue_type,
                    },
                    ensure_ascii=False,
                )
            )
    return all_avail_problems


def get_problem_instance(problem_id: str) -> TaskBase:
    """Get the problem instance by ID.

    Args:
        problem_id: The problem ID.

    Returns:
        The problem instance.
    """
    if problem_id in _PROBLEMS:
        return _PROBLEMS[problem_id]()
    else:
        return None


def get_submission_template(problem_id: str) -> BaseModel:
    """Get the submission template for a specific problem.

    Args:
        problem_id (str): The ID of the problem.

    Returns:
        BaseModel: The submission template for the problem.
    """
    if problem_id in _PROBLEMS:
        return _PROBLEMS[problem_id].SUBMISSION
    else:
        return None


if __name__ == "__main__":
    # print(get_submission_template("frr_down_detection"))
    print(list_avail_problems("frr_down_localization"))
