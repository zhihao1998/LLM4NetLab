import asyncio
import logging
import operator

from dotenv import load_dotenv
from langchain.messages import AnyMessage
from typing_extensions import Annotated, TypedDict

from agent.utils.loggers import FileLoggerHandler
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.orchestrator.problems.problem_base import TaskLevel

load_dotenv()


class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[list[AnyMessage], operator.add]
    ready_submit: bool


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    backend_model_name = "qwen3:32b"
    root_cause_name = "frr_service_down"
    task_level = TaskLevel.DETECTION
    root_cause_category, task_desc, session_id, lab_name = orchestrator.init_problem(root_cause_name, task_level)

    result = await troubleshooting_agent.ainvoke(
        {"messages": [f"Your task is described as follows: {task_desc}"]},
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
    )
    print("Final result:", result)

    # 6. Evaluation
    # orchestrator.eval_problem()

    # 7. Stop problem and cleanup
    orchestrator.stop_problem(cleanup=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
