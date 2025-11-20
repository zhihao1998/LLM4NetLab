import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from llm4netlab.orchestrator.problems.prob_pool import list_avail_root_causes as _list_avail_root_causes
from llm4netlab.orchestrator.tasks.detection import DetectionSubmission
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission
from llm4netlab.orchestrator.tasks.rca import RCASubmission

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
BACKEND_MODEL_NAME = os.getenv("BACKEND_MODEL_NAME")
AGENT_NAME = os.getenv("AGENT_NAME")

base_dir = os.getenv("BASE_DIR")
results_dir = os.getenv("RESULTS_DIR")


@mcp.tool()
def list_avail_root_causes() -> list[str]:
    """List all available root cause types.

    Returns:
        list[str]: A list of available root cause types.
    """
    return _list_avail_root_causes()


@mcp.tool()
def get_submission_template() -> str:
    """Get the submission instruction for a specific problem.

    Returns:
        str: The submission instruction.
    """
    if TASK_LEVEL == "detection":
        template = DetectionSubmission.model_json_schema()
    elif TASK_LEVEL == "localization":
        template = LocalizationSubmission.model_json_schema()
    elif TASK_LEVEL == "rca":
        template = RCASubmission.model_json_schema()
    else:
        raise ValueError(f"Unsupported task level: {TASK_LEVEL}")
    return json.dumps(template)


@mcp.tool()
def submit(submission: Dict[str, Any]) -> List[str]:
    """Submit a task solution. Before submission, call get_submission_template to get the expected submission format.

    Args:
        submission: The submission data for the task.

    Returns:
        bool: Indicates whether the submission was successful.
    """
    # record the result for evaluation
    submission["backend_model_name"] = BACKEND_MODEL_NAME
    submission["agent_name"] = AGENT_NAME
    os.makedirs(
        f"{results_dir}/{ROOT_CAUSE_CATEGORY}/{ROOT_CAUSE_NAME}/{TASK_LEVEL}/",
        exist_ok=True,
    )
    with open(
        f"{results_dir}/{ROOT_CAUSE_CATEGORY}/{ROOT_CAUSE_NAME}/{TASK_LEVEL}/{LAB_SESSION_ID}_{BACKEND_MODEL_NAME}_submission.log",
        "a+",
    ) as log_file:
        log_file.write(json.dumps(submission))

    return ["Submission success."]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
