import asyncio
import logging
import operator
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import AnyMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing_extensions import Annotated, TypedDict

from agent.llm.model_factory import load_default_model
from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig
from agent.utils.template import TROUBLE_SHOOTING_PROMPT
from llm4netlab.config import RESULTS_DIR
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.orchestrator.problems.problem_base import TaskLevel

load_dotenv()


class TaskState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    ready_submit: bool


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    backend_model_name = "qwen3:32b"
    root_cause_type = "frr_service_down"
    task_level = TaskLevel.DETECTION
    root_cause_category, task_desc, session_id, lab_name = orchestrator.init_problem(root_cause_type, task_level)

    # 2. Load MCP server and client
    mcp_server_config = MCPServerConfig(
        session_id=session_id,
        root_cause_type=root_cause_type,
        task_level=task_level,
        lab_name=lab_name,
        backend_model_name=backend_model_name,
        agent_name="ReAct",
    ).load_config()["mcpServers"]

    # 3. Create MCP client
    log_path = os.path.join(
        f"{RESULTS_DIR}/{root_cause_category}/{root_cause_type}/{session_id}_{backend_model_name}_conversation.log"
    )
    client = MultiServerMCPClient(connections=mcp_server_config)

    llm = load_default_model()

    tools = await client.get_tools()

    troubleshooting_agent = create_agent(
        model=llm,
        system_prompt=TROUBLE_SHOOTING_PROMPT,
        tools=tools,
    )
    result = await troubleshooting_agent.ainvoke(
        {"messages": [f"Your task is described as: {task_desc}"], "llm_calls": 0},
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
    )
    print("Final result:", result)

    # 6. Evaluation
    orchestrator.eval()

    # 7. Stop problem and cleanup
    orchestrator.stop_problem(cleanup=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
