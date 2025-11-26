from enum import StrEnum

from pydantic import BaseModel


class RootCauseCategory(StrEnum):
    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    LINK_FAILURE = ("link_failure", "Link failures: physical disconnections, interface down")
    END_HOST_FAILURE = ("end_host_failure", "Host misconfiguration: IP, gateway, DNS, DHCP issues")
    NETWORK_NODE_ERROR = ("network_node_error", "Router/switch crashes, reboots, high CPU/memory usage")
    RESOURCE_CONTENTION = ("resource_contention", "Resource contention: bandwidth saturation, buffer overflows")
    MISCONFIGURATION = ("misconfiguration", "Configuration errors: wrong IP, ACL, routing protocol settings")
    NETWORK_UNDER_ATTACK = ("network_under_attack", "Security attacks: DDoS, BGP hijack, MITM, spoofing")
    MULTIPLE_FAULTS = ("multiple_faults", "Multiple simultaneous faults in the network")


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
