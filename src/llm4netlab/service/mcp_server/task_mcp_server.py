import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from llm4netlab.orchestrator.problems.prob_pool import get_submission_template as _get_submission_template
from llm4netlab.orchestrator.problems.prob_pool import (
    list_avail_root_cause_categories as _list_avail_root_cause_categories,
)
from llm4netlab.orchestrator.problems.prob_pool import list_avail_root_cause_types as _list_avail_root_cause_types

# Initialize FastMCP server
mcp = FastMCP(
    "task_mcp_server",
    instructions="This mcp server contains the apis to interact with tasks, for now using to submit your solution.",
)


# message returned to agent after submission, not used for now
# class SubmissionOutput(BaseModel):
#     success: bool = Field(description="Indicates whether the submission was successful.")
#     message: str = Field(description="Submission message.")
load_dotenv(verbose=True)

# The following environment variables should be passed from the MCP client (i.e., the agent)
LAB_SESSION_ID = os.getenv("LAB_SESSION_ID")
ROOT_CAUSE_TYPE = os.getenv("ROOT_CAUSE_TYPE")
TASK_LEVEL = os.getenv("TASK_LEVEL")
BACKEND_MODEL_NAME = os.getenv("BACKEND_MODEL_NAME")
AGENT_NAME = os.getenv("AGENT_NAME")

base_dir = os.getenv("BASE_DIR")
results_dir = os.getenv("RESULTS_DIR")


@mcp.tool()
def list_avail_root_cause_categories() -> list[str]:
    """List available root cause categories.

    Returns:
        list[str]: List of available root cause categories.
    """
    return _list_avail_root_cause_categories()


@mcp.tool()
def list_avail_root_cause_types(root_cause_category: str) -> list[str]:
    """List available root cause types for a specific root cause category.

    Args:
        root_cause_category (str): The root cause category.
    Returns:
        list[str]: List of available root cause types.
    """

    return _list_avail_root_cause_types(root_cause_category)


@mcp.tool()
def get_submission_template(root_cause_type: str) -> str:
    """Get the submission instruction for a specific problem.

    Args:
        root_cause_type: The root cause type.

    Returns:
        str: The submission instruction.
    """
    return _get_submission_template(root_cause_type, task_level=TASK_LEVEL)


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

    with open(
        f"{results_dir}/{ROOT_CAUSE_TYPE}/{LAB_SESSION_ID}_{BACKEND_MODEL_NAME}_submission.log", "a+"
    ) as log_file:
        log_file.write(json.dumps(submission))

    return ["Submission success."]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
