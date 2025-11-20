from enum import StrEnum

from pydantic import BaseModel


class RootCauseCategory(StrEnum):
    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    DEVICE_FAILURE = ("device_failure", "Hardware or interface/module failure")
    END_HOST_MISCONFIGURATION = ("end_host_misconfiguration", "Host misconfiguration: IP, gateway, DNS, DHCP issues")
    PERFORMANCE_DEGRADATION = ("performance_degradation", "High latency, packet loss, jitter, throughput drop")
    SERVICE_DEPENDENCY_FAILURE = ("service_dependency_failure", "External dependency: DNS, NTP, AAA, PKI")

    DATA_PLANE_ISSUE = ("data_plane_forwarding_issue", "Routing/forwarding blackhole, loop, asymmetry")

    CONFIG_ROUTING_POLICY_ERROR = ("config_routing_policy_error", "Wrong BGP/OSPF/EVPN policy, metric misconfig")

    CONFIG_ACCESS_POLICY_ERROR = ("config_access_policy_error", "ACL / firewall / security group misconfig")

    SECURITY_POLICY_BLOCK = ("security_policy_block", "Legitimate traffic blocked by security rule")
    RESOURCE_EXHAUSTION = ("resource_exhaustion", "CPU/memory/TCAM/FIB exhaustion, NAT pool depletion")

    # --- P4 / SDN specific ---
    P4_PIPELINE_MISCONFIG = ("p4_pipeline_misconfig", "Wrong parser/match-action table, compile/load errors")
    P4_RUNTIME_ERROR = ("p4_runtime_error", "P4 runtime update fails, table entry inconsistency")
    SDN_CONTROLLER_FAILURE = ("sdn_controller_failure", "Controller crash, southbound API loss")
    SDN_RULE_CONFLICT = ("sdn_rule_conflict", "SDN flow rule overlap/shadowing causes blackhole/loop")


class TaskLevel(StrEnum):
    DETECTION = "detection"
    LOCALIZATION = "localization"
    RCA = "rca"


class TaskDescription(StrEnum):
    DETECTION = "Detect if there is an anomaly in the network. Return True if an anomaly is present, otherwise False."
    LOCALIZATION = "Localize the faulty component(s) in the network. Pinpoint where the anomaly occurs."
    RCA = "Identify the root cause of the anomaly in the network. Explain why the anomaly occurred."


class ProblemMeta(BaseModel):
    root_cause_category: RootCauseCategory
    root_cause_name: str
    task_level: TaskLevel
    description: str
