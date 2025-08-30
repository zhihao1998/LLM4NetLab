import asyncio
import logging

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.orchestrator.orchestrator import Orchestrator


class AgentWithMCP(AgentBase):
    def __init__(self, name, llm, client, max_steps, system_prompt_template):
        super().__init__()
        self.name = name
        self.agent = MCPAgent(
            llm=llm, client=client, max_steps=max_steps, system_prompt_template=system_prompt_template, verbose=True
        )

    async def arun(self, query: str) -> str:
        """
        Asynchronous run method to process a query.
        """
        return await self.agent.run(query)


async def main():
    # Load environment variables
    load_dotenv("/home/p4/codes/AI4NetOps/.env")

    # Create configuration dictionary
    config = {
        "mcpClient": {
            "name": "MCPAgent_DeepSeek",
            "session_id": "session_123"
        },
        "mcpServers": {
            "kathara_base_mcp_server": {
                "command": "python3",
                "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_base_mcp_server.py"],
            },
            # "kathara_bmv2_mcp_server": {
            #     "command": "python3",
            #     "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_bmv2_mcp_server.py"],
            # },
            # "kathara_telemetry_mcp_server": {
            #     "command": "python3",
            #     "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_telemetry_mcp_server.py"],
            # },
            # "common_tools_mcp_server": {
            #     "command": "python3",
            #     "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/common_tools_mcp_server.py"],
            # },
            "kathara_frr_mcp_server": {
                "command": "python3",
                "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_frr_mcp_server.py"],
            },
            "task_mcp_server": {
                "command": "python3",
                "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/task_mcp_server.py"],
            },
        }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)
    client.
    # Create LLM
    llm = ChatDeepSeek(model="deepseek-reasoner")
    # Create agent with the client
    agent = AgentWithMCP(
        name="MCPAgent_DeepSeek",
        llm=llm,
        client=client,
        max_steps=20,
        system_prompt_template=MCP_PROMPT_TEMPLATE,
    )

    orchestrator = Orchestrator()
    task_desc = orchestrator.init_problem("frr_down_detection")
    orchestrator.register_agent(agent, agent.name)

    # Run the query
    result = await agent.arun(task_desc)
    print("\n\nFinal Result:", result)

    orchestrator.stop_problem(cleanup=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
