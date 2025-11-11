from enum import StrEnum

from pydantic import BaseModel


class IssueType(StrEnum):
    DEVICE_FAILURE = "device_failure"  # Hardware or interface/module failure
    PERFORMANCE_DEGRADATION = "performance_degradation"  # High latency, packet loss, jitter, throughput drop

    CONTROL_PLANE_FAILURE = "control_plane_failure"  # Routing/neighbor flap, convergence issues
    DATA_PLANE_ANOMALY = "data_plane_anomaly"  # Forwarding anomalies: blackhole, ECMP imbalance, MTU mismatch

    CONFIG_ROUTING_POLICY_ERROR = "config_routing_policy_error"  # Wrong BGP/OSPF/EVPN policy, metric misconfig
    CONFIG_ACCESS_POLICY_ERROR = "config_access_policy_error"  # ACL / firewall / security group misconfig
    CONFIG_TOPOLOGY_ERROR = "config_topology_error"  # VLAN mismatch, trunk misconfig, spanning tree
    CONFIG_HOST_ERROR = "config_host_error"  # Host misconfig: IP, gateway, DNS, DHCP issues

    SECURITY_POLICY_BLOCK = "security_policy_block"  # Legitimate traffic blocked by security rule
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # CPU/memory/TCAM/FIB exhaustion, NAT pool depletion
    DEPENDENCY_FAILURE = "dependency_failure"  # External dependency: DNS, NTP, AAA, PKI

    # --- P4 / SDN specific ---
    P4_PIPELINE_MISCONFIG = "p4_pipeline_misconfig"  # Wrong parser/match-action table, compile/load errors
    P4_RUNTIME_ERROR = "p4_runtime_error"  # Runtime update fails, table entry inconsistency
    SDN_CONTROLLER_FAILURE = "sdn_controller_failure"  # Controller crash, southbound API loss
    SDN_RULE_CONFLICT = "sdn_rule_conflict"  # Flow rule overlaps or shadowing causes blackhole/loop


class ProblemLevel(StrEnum):
    DISCOVERY = "discovery"
    DETECTION = "detection"
    LOCALIZATION = "localization"
    MITIGATION = "mitigation"


class ProblemMeta(BaseModel):
    id: str
    description: str
    issue_type: IssueType
    problem_level: ProblemLevel
