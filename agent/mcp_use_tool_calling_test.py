import asyncio
import logging

from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.orchestrator.problems.problem_base import IssueType


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
            # "kathara_frr_mcp_server": {
            #     "command": "python3",
            #     "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_frr_mcp_server.py"],
            # },
            "task_mcp_server": {
                "command": "python3",
                "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/task_mcp_server.py"],
                "env": {
                    "LAB_SESSION_ID": session_id,
                    "LAB_PROBLEM_ID": problem_id,
                    "LAB_NAME": lab_name,
                    "AGENT_NAME": "AgentWithMCP",
                },
            },
        },
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)
    # Create LLM
    # llm = ChatDeepSeek(model="deepseek-reasoner")
    # # Create agent with the client
    # agent = AgentWithMCP(
    #     name="MCPAgent_DeepSeek",
    #     llm=llm,
    #     client=client,
    #     max_steps=20,
    #     system_prompt_template=MCP_PROMPT_TEMPLATE,
    # )

    await client.create_all_sessions()
    session = client.get_session("task_mcp_server")
    tools = await session.list_tools()
    print("Available tools:", tools)

    result = await session.call_tool(
        name="list_avail_problems",
        arguments={},
    )
    print("get_avail_problems call result:", result)
    print()

    result = await session.call_tool(
        name="get_submission_template",
        arguments={"problem_id": problem_id},
    )
    print("get_submission_template call result:", result)
    print()

    result = await session.call_tool(
        name="submit",
        arguments={
            "submission": {
                "is_anomaly": True,
                "issue_type": IssueType.DEVICE_FAILURE,
                "problem_id": problem_id,
            }
        },
    )
    print("submit_detection call result:", result)
    print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
