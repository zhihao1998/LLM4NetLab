import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.utils.loggers import FileLoggerHandler

# Load environment variables
load_dotenv()

# load paths
base_dir = os.getenv("BASE_DIR")
assert base_dir is not None, "BASE_DIR environment variable is not set."
result_dir = os.path.join(base_dir, "results")
mcp_server_dir = os.path.join(base_dir, "llm4netlab/service/mcp_server")


# define agent
class AgentWithMCP(AgentBase):
    def __init__(self, name, llm, client, max_steps, system_prompt_template, log_dir):
        super().__init__()
        self.name = name
        self.agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=max_steps,
            system_prompt_template=system_prompt_template,
            verbose=True,
            callbacks=[FileLoggerHandler(log_dir)],
        )

    async def arun(self, query: str) -> str:
        """
        Asynchronous run method to process a query.
        """
        return await self.agent.run(query)


async def main():
    orchestrator = Orchestrator()
    task_desc = orchestrator.init_problem("frr_down_detection")

    session_id = orchestrator.session.session_id
    problem_id = orchestrator.problem_id
    lab_name = orchestrator.problem.net_env.name

    # Create configuration dictionary
    config = {
        "mcpServers": {
            "kathara_base_mcp_server": {
                "command": "python3",
                "args": [f"{mcp_server_dir}/kathara_base_mcp_server.py"],
            },
            "kathara_bmv2_mcp_server": {
                "command": "python3",
                "args": [f"{mcp_server_dir}/kathara_bmv2_mcp_server.py"],
            },
            "kathara_telemetry_mcp_server": {
                "command": "python3",
                "args": [f"{mcp_server_dir}/kathara_telemetry_mcp_server.py"],
            },
            "common_tools_mcp_server": {
                "command": "python3",
                "args": [f"{mcp_server_dir}/common_tools_mcp_server.py"],
            },
            "kathara_frr_mcp_server": {
                "command": "python3",
                "args": [f"{mcp_server_dir}/kathara_frr_mcp_server.py"],
            },
            "task_mcp_server": {
                "command": "python3",
                "args": [f"{mcp_server_dir}/task_mcp_server.py"],
            },
        },
    }

    # add env to every server
    for server in config["mcpServers"].values():
        server["env"] = {
            "LAB_SESSION_ID": session_id,
            "LAB_PROBLEM_ID": problem_id,
            "LAB_NAME": lab_name,
            "AGENT_NAME": "AgentWithMCP",
        }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatDeepSeek(model="deepseek-reasoner")
    # Create agent with the client
    agent = AgentWithMCP(
        name="MCPAgent_DeepSeek",
        llm=llm,
        client=client,
        max_steps=20,
        system_prompt_template=MCP_PROMPT_TEMPLATE,
        log_dir=os.path.join(result_dir, problem_id, session_id + "_chat.log"),
    )

    orchestrator.register_agent(agent, agent.name)

    # Run the query
    result = await agent.arun(task_desc)
    print("\n\nFinal Result:", result)

    orchestrator.stop_problem(cleanup=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
