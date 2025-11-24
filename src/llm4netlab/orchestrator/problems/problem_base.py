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
    SDN_CONTROL_PLANE_ISSUE = (
        "sdn_control_plane_issue",
        "SDN controller unreachable/crash, flow rule missing/conflict",
    )
    P4_PIPELINE_ISSUE = ("p4_pipeline_issue", "P4 program bug, table miss, action misconfiguration")
    ROUTING_POLICY_MISCONFIGURATION = (
        "routing_policy_misconfiguration",
        "Wrong BGP/OSPF policy, metric misconfig",
    )
    ACCESS_POLICY_MISCONFIGURATION = ("access_policy_misconfiguration", "ACL / firewall / security group misconfig")
    MULTIPLE_FAULTS = ("multiple_faults", "Multiple simultaneous faults in the network")
    SWITCH_FORWARDING_ERRORS = ("switch_forwarding_errors", "Switch forwarding errors due to misconfigurations or bugs")


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
