"""Define and query information about an Detection task."""

import textwrap
from typing import Annotated, Literal

from pydantic import BaseModel, Field, ValidationError

from llm4netlab.orchestrator.tasks.base import TaskBase


class DeviceComponent(BaseModel):
    type: Literal["device"] = Field("device", description="Component type, must be 'device'.")
    device_name: str = Field(..., description="Device name. Example: 'router_1'.")


class PortComponent(BaseModel):
    type: Literal["port"] = Field("port", description="Component type, must be 'port'.")
    device_name: str = Field(..., description="Device name. Example: 'router_1'.")
    port_name: str = Field(..., description="Port name on the device. Example: 'eth0'.")


class LinkComponent(BaseModel):
    type: Literal["link"] = Field("link", description="Component type, must be 'link'.")
    src_device: str = Field(..., description="Source device name. Example: 'router_1'.")
    dst_device: str = Field(..., description="Destination device name. Example: 'router_2'.")


class ServiceComponent(BaseModel):
    type: Literal["service"] = Field("service", description="Component type, must be 'service'.")
    service_name: Literal["frr", "quagga", "named", "dhcpd", "httpd", "bgpd", "ospfd"] = Field(
        ...,
        description="Service name. Example: 'bgpd'.",
    )


LocalizationComponent = Annotated[
    DeviceComponent | PortComponent | LinkComponent | ServiceComponent,
    Field(discriminator="type"),
]


class LocalizationSubmission(BaseModel):
    target_components: list[LocalizationComponent] = Field(
        ...,
        description=textwrap.dedent("""\
            List of localized components that are identified as faulty. Each item must be one of
            DeviceComponent, PortComponent, LinkComponent, ServiceComponent. Examples:
            [
                {
                    "type": "device",
                    "device_name": "router_1",
                },
                {
                    "type": "link",
                    "src_device": "router_1",
                    "dst_device": "router_2",
                },
            ]
        """),
    )


class LocalizationTask(TaskBase):
    def __init__(self):
        super().__init__()
        self.task_desc = """\
            The network you are working with is described below:
            {net_desc}

            The following symptoms have been observed in the network (if any):
            {symptom_desc}

            Your task is to localize the anomaly.
            Pinpoint the faulty component(s), such as device, interface, link, prefix, neighbor, or path segment.
            Focus strictly on *where* the anomaly occurs.

            Do not analyze or speculate about root causes. Do not propose mitigations.
            """

    def eval(self, submission: dict) -> float:
        """Evaluate the localization task submission.

        Args:
            submission: The submission to evaluate. Expected schema:
                {
                    "target_components": [
                        {
                            "type": "device",
                            "device_name": "<device_id>"
                        }
                        | {
                            "type": "port",
                            "device_name": "<device_id>",
                            "port_name": "<port_name>"
                        }
                        | {
                            "type": "link",
                            "src_device": "<src_device_id>",
                            "dst_device": "<dst_device_id>"
                        }
                        | {
                            "type": "service",
                            "service_name": "frr|quagga|named|dhcpd|httpd|bgpd|ospfd"
                        },
                        ...
                    ]
                }

        Returns:
            float: The evaluation score in [0, 1], or -1.0 if submission is invalid.
        """
        # 1. Validate submission schema
        try:
            parsed_submission = LocalizationSubmission.model_validate(submission)
        except ValidationError:
            return -1.0

        submitted_components = parsed_submission.target_components

        # 2. normalize components for comparison
        def normalize_component(comp: "LocalizationComponent") -> tuple:
            """
            Normalize a component into a comparable tuple key.

            Returns:
              - device:  ("device", device_name)
              - port:    ("port", device_name, port_name)
              - service: ("service", service_name)
              - link:    ("link", min(src_device, dst_device), max(src_device, dst_device))
            """
            data = comp.model_dump()
            ctype = data.get("type")

            if ctype == "device":
                return ("device", data.get("device_name"))

            if ctype == "port":
                return ("port", data.get("device_name"), data.get("port_name"))

            if ctype == "service":
                return ("service", data.get("service_name"))

            if ctype == "link":
                src = data.get("src_device")
                dst = data.get("dst_device")
                if not src or not dst:
                    return ("link", None, None)
                a, b = sorted([src, dst])
                return ("link", a, b)

            return ("unknown", None)

        # 3. Get ground truth components
        gt = getattr(self, "SUBMISSION", None)

        gt_components_raw = gt.target_components

        # 4. Get normalized component sets
        correct_components = {normalize_component(c) for c in gt_components_raw}
        submitted_components_norm = {normalize_component(c) for c in submitted_components}

        # 5. Calculate precision, recall, F1 score
        tp = len(correct_components & submitted_components_norm)
        fp = len(submitted_components_norm - correct_components)
        fn = len(correct_components - submitted_components_norm)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)

        return float(f1)


if __name__ == "__main__":
    task = LocalizationSubmission(
        target_components=[
            {
                "type": "device",
                "device_name": "router_1",
            },
            {
                "type": "link",
                "src_device": "router_1",
                "dst_device": "router_2",
            },
        ]
    )
    print(task.model_json_schema())

    print(task)
