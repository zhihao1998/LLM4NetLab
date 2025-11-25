import json
import os
from typing import List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from llm4netlab.orchestrator.problems.prob_pool import list_avail_problem_names as _list_avail_problems
from llm4netlab.orchestrator.tasks.localization import LocalizationSubmission
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
backend_model = os.getenv("backend_model")
agent_type = os.getenv("agent_type")

base_dir = os.getenv("BASE_DIR")
results_dir = os.getenv("RESULTS_DIR")


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
def submit(submission: LocalizationSubmission) -> List[str]:
    """Submit a task solution.

    Args:
        submission (LocalizationSubmission): The submission data.

    Returns:
        List[str]: Submission status messages.
    """
    submission_dict = submission.model_dump()

    submission_dict["backend_model"] = backend_model
    submission_dict["agent_type"] = agent_type
    os.makedirs(
        f"{results_dir}/{ROOT_CAUSE_NAME}/{TASK_LEVEL}/{LAB_SESSION_ID}",
        exist_ok=True,
    )
    with open(
        f"{results_dir}/{ROOT_CAUSE_NAME}/{TASK_LEVEL}/{LAB_SESSION_ID}/{backend_model}_submission.log",
        "a+",
    ) as log_file:
        log_file.write(json.dumps(submission_dict))

    return ["Submission success."]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
