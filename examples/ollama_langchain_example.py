import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.config import RESULTS_DIR
from llm4netlab.orchestrator.orchestrator import Orchestrator

load_dotenv()


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    backend_model_name = "qwen3:32b"

    task_desc, session_id, root_cause_name, lab_name = orchestrator.init_problem("frr_down_localization")
    # 2. Load MCP server and client
    mcp_server_config = MCPServerConfig(
        backend_model_name=backend_model_name,
        session_id=session_id,
        root_cause_name=root_cause_name,
        lab_name=lab_name,
    ).load_config()["mcpServers"]

    # 3. Create MCP client
    log_path = os.path.join(f"{RESULTS_DIR}/{root_cause_name}/{session_id}_{backend_model_name}_conversation.log")
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

    # log_path = os.path.join(f"{RESULTS_DIR}/{root_cause_name}/{session_id}_{backend_model_name}_conversation.log")
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
