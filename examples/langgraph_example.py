import asyncio
import logging
import operator
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import AnyMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from typing_extensions import Annotated, TypedDict

from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.config import RESULTS_DIR
from llm4netlab.orchestrator.orchestrator import Orchestrator

load_dotenv()


class TaskState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    ready_submit: bool


def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


from langchain.messages import ToolMessage


def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    backend_model_name = "qwen3:32b"

    task_desc, session_id, root_cause_type, lab_name = orchestrator.init_problem("frr_down_localization")
    # 2. Load MCP server and client
    mcp_server_config = MCPServerConfig(
        backend_model_name=backend_model_name,
        session_id=session_id,
        root_cause_type=root_cause_type,
        lab_name=lab_name,
    ).load_config()["mcpServers"]

    # 3. Create MCP client
    log_path = os.path.join(f"{RESULTS_DIR}/{root_cause_type}/{session_id}_{backend_model_name}_conversation.log")
    client = MultiServerMCPClient(connections=mcp_server_config)

    llm = ChatOllama(
        model=backend_model_name,
        temperature=0,
        validate_model_on_init=True,
        base_url=os.getenv("OLLAMA_API_URL"),
        callbacks=[FileLoggerHandler(log_path=log_path)],
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=llm,
        system_prompt=MCP_PROMPT_TEMPLATE.format(tool_descriptions=tools),
        tools=tools,
    )

    math_response = await agent.run()
    print("math_response:", math_response)

    # 4. Create and register Agent

    # log_path = os.path.join(f"{RESULTS_DIR}/{root_cause_type}/{session_id}_{backend_model_name}_conversation.log")
    # agent = AgentWithMCP(
    #     agent_name=f"ReAct_Ollama_{backend_model_name}",
    #     backend_model=backend_model_name,
    #     llm=llm,
    #     client=client,
    #     max_steps=20,
    #     log_path=log_path,
    # )
    # orchestrator.register_agent(agent)

    # # 5. GO
    # result = await agent.arun(task_desc)
    # print("\n\nFinal Result:", result)

    # # 6. Evaluation
    # orchestrator.eval()

    # # 7. Stop problem and cleanup
    # orchestrator.stop_problem(cleanup=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
