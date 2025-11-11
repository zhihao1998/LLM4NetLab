import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from llm4netlab.orchestrator.problems.prob_pool import get_submission_template as _get_submission_template
from llm4netlab.orchestrator.problems.prob_pool import list_avail_problems as _list_avail_problems

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

LAB_SESSION_ID = os.getenv("LAB_SESSION_ID")
LAB_PROBLEM_ID = os.getenv("LAB_PROBLEM_ID")
MODEL_NAME = os.getenv("MODEL_NAME")
base_dir = os.getenv("BASE_DIR")
results_dir = os.getenv("RESULTS_DIR")
assert base_dir is not None, "BASE_DIR environment variable is not set."
assert results_dir is not None, "RESULTS_DIR environment variable is not set."

@mcp.tool()
def list_avail_problems() -> list[str]:
    """List available problems and their related information.

    Returns:
        list[(problem_id: str, problem_description: str, issue_type: str)]: A list of (problem_id, problem_description, issue_type) tuples.
    """

    return _list_avail_problems(LAB_PROBLEM_ID)


@mcp.tool()
def get_submission_template(problem_id: str) -> dict:
    """Get the submission template for a specific problem.

    Args:
        problem_id (str): The ID of the problem.

    Returns:
        dict: The submission inputSchema for the problem.
    """
    return _get_submission_template(problem_id).model_json_schema()


@mcp.tool()
def submit(submission: Dict[str, Any]) -> List[str]:
    """Submit a detection task solution.

    Args:
        submission: The submission data for the detection task.

    Returns:
        str: The result of the submission.
    """
    sub_template: BaseModel = _get_submission_template(submission["problem_id"])
    if not sub_template:
        return ["Submission validation failed: Invalid problem ID."]

    # validate the submission
    try:
        validated = sub_template.model_validate(submission)
    except Exception as e:
        return [f"Submission validation failed: {e}"]

    # record the result for evaluation
    result = validated.model_dump()
    result["model"] = MODEL_NAME

    with open(f"{results_dir}/{LAB_PROBLEM_ID}/{LAB_SESSION_ID}_submission.log", "a+") as log_file:
        log_file.write(json.dumps(result))

    return ["Detection submission successful."]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
