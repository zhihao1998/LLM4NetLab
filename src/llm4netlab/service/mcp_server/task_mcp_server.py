import json
import os
from typing import List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from llm4netlab.orchestrator.problems.prob_pool import list_avail_problem_names as _list_avail_problems
from llm4netlab.utils.errors import safe_tool

# Initialize FastMCP server
mcp = FastMCP(
    "task_mcp_server",
    instructions="This mcp server contains the apis to interact with tasks, for now using to submit your solution.",
)

load_dotenv(verbose=True)

# The following environment variables should be passed from the MCP client (i.e., the agent)
LAB_SESSION_ID = os.getenv("LAB_SESSION_ID")
ROOT_CAUSE_CATEGORY = os.getenv("ROOT_CAUSE_CATEGORY")
ROOT_CAUSE_NAME = os.getenv("ROOT_CAUSE_NAME")
TASK_LEVEL = os.getenv("TASK_LEVEL")

base_dir = os.getenv("BASE_DIR")
results_dir = os.getenv("RESULTS_DIR")


class SubmissionFormat(BaseModel):
    is_anomaly: bool = Field(..., description="Indicates whether an anomaly was detected.")
    faulty_devices: List[str] = Field(
        ...,
        description=(
            "List of localized devices that are identified as faulty. "
            "Each item is a device name (string). "
            "Example: ['router_1', 'switch_2']"
        ),
    )
    root_cause_name: List[str] = Field(
        ...,
        description=(
            "The name(s) of the identified root cause(s) of the network anomaly. "
            "MUST be from the provided list of root cause names. "
            "Get the names from the 'list_avail_problems()' tool.",
        ),
    )


@safe_tool
@mcp.tool()
def list_avail_problems() -> list[str]:
    """List all available root cause types.

    Returns:
        list[str]: A list of available root cause types.
    """
    return _list_avail_problems()


@safe_tool
@mcp.tool()
def submit(
    is_anomaly: bool,
    faulty_devices: List[str],
    root_cause_name: List[str],
) -> List[str]:
    """
    Submit a task solution.

    Args:
        is_anomaly: Indicates whether an anomaly was detected.
        faulty_devices: List of localized devices that are identified as faulty.
        root_cause_name: The name(s) of the identified root cause(s) of the network anomaly. MUST be selected from the result of 'list_avail_problems' tool.
    """
    submission_dict = {
        "is_anomaly": is_anomaly,
        "faulty_devices": faulty_devices,
        "root_cause_name": root_cause_name,
    }
    os.makedirs(
        f"{results_dir}/{ROOT_CAUSE_NAME}/{LAB_SESSION_ID}",
        exist_ok=True,
    )
    with open(f"{results_dir}/{ROOT_CAUSE_NAME}/{LAB_SESSION_ID}/submission.json", "w+") as log_file:
        log_file.write(json.dumps(submission_dict))

    return ["Submission success."]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
