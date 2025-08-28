"""
Each problem must have at least one network environment and one task.
"""

from llm4netlab.orchestrator.problems.bgp_failures.bgp_peer_failure import (
    BgpAclBlockDetection,
    BgpAsnMisconfigDetection,
)
from llm4netlab.orchestrator.problems.device_down.bmv2_down import Bmv2DownDetection
from llm4netlab.orchestrator.problems.device_down.frr_down import FrrDownDetection
from llm4netlab.orchestrator.problems.intf_packet_loss.intf_packet_loss import (
    PacketLossDetection,
)
from llm4netlab.orchestrator.problems.ospf_failures.ospf_peer_failure import (
    OspfAclBlockDetection,
    OspfMisconfigDetection,
)
from llm4netlab.orchestrator.problems.p4_failures.p4_tbl_entry_missing import (
    P4TableEntryMissingDetection,
)
from llm4netlab.orchestrator.problems.performance_failure.int import (
    P4IntHopDelayHighDetection,
)
from llm4netlab.orchestrator.tasks.base import TaskBase

_PROBLEMS = {
    ####################
    #  Generic device failure issues
    ####################
    "frr_down_detection": FrrDownDetection,
    "bmv2_down_detection": Bmv2DownDetection,
    ####################
    #  BGP issues
    ####################
    # ref: https://support.huawei.com/enterprise/en/doc/EDOC1000177634/31f2a647/case-study-a-bgp-peer-relationship-fails-to-be-established#EN-US_CONCEPT_0000001180501803
    # An ACL filters out the packets carrying TCP port 179.
    "bgp_acl_block_detection": BgpAclBlockDetection,
    # ASN misconfiguration can cause BGP peer relationship to fail.
    "bgp_asn_misconfig_detection": BgpAsnMisconfigDetection,
    ####################
    #  OSPF issues
    ####################
    "ospf_acl_block_detection": OspfAclBlockDetection,
    # OSPF area misconfiguration can cause routing issues.
    "ospf_misconfig_detection": OspfMisconfigDetection,
    ####################
    #  P4 issues
    ####################
    "p4_tbl_entry_missing_detection": P4TableEntryMissingDetection,
    ####################
    #  INT issues
    ####################
    "p4_int_hop_delay_high_detection": P4IntHopDelayHighDetection,
    ####################
    #  Generic issues
    ####################
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
