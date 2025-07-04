"""
Each problem must have at least one network environment and one task.
"""

from llm4netlab.orchestrator.problems.intf_packet_loss.intf_packet_loss import (
    PacketLossDetection,
    PacketLossDiscovery,
)
from llm4netlab.orchestrator.problems.p4_tbl_entry_missing.p4_tbl_entry_missing import (
    P4TableEntryMissingDetection,
    P4TableEntryMissingDiscovery,
)
from llm4netlab.orchestrator.tasks.base import TaskBase

_PROBLEMS = {
    # basic table entry missing problem
    "p4_tbl_entry_missing_discovery": P4TableEntryMissingDiscovery,
    "p4_tbl_entry_missing_detection": P4TableEntryMissingDetection,
    "packet_loss_discovery": PacketLossDiscovery,
    "packet_loss_detection": PacketLossDetection,
}


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
        raise ValueError(f"Problem ID {problem_id} not found in the pool.")
