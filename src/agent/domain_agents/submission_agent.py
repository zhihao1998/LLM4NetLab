import asyncio
import logging
from textwrap import dedent

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools.structured import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.llm.model_factory import load_model
from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig

load_dotenv()

SUBMIT_PROMPT_TEMPLATE = dedent("""\
    You are an expert network engineer.
    Your task is to submit the final solution for this network problem based on the diagnosis reported provided.
    Carefully review the diagnosis results and ensure that your submission is accurate and complete.
    You must strictly follow the submission format and call the submit() tool to submit your solution.
""").strip()


class SubmissionAgent:
    def __init__(self, backend_model: str = "gpt-oss:20b"):
        mcp_server_config = MCPServerConfig().load_config(if_submit=True)
        self.client = MultiServerMCPClient(connections=mcp_server_config)
        self.tools = None

        self.llm = load_model(backend_model=backend_model)

    async def load_tools(self):
        self.tools: list[StructuredTool] = await self.client.get_tools()
        for tool in self.tools:
            tool.handle_tool_error = True
            tool.handle_validation_error = True

    def get_agent(self):
        """Final submission node"""
        agent = create_agent(
            model=self.llm, system_prompt=SUBMIT_PROMPT_TEMPLATE, tools=self.tools, name="SubmissionAgent"
        )
        return agent


async def run_submission_agent():
    logging.basicConfig(level=logging.INFO)

    submission_agent = SubmissionAgent()
    await submission_agent.load_tools()

    graph = submission_agent.get_agent()
    inputs = {
        "messages": ["There is a failed FRR service on router1. Please submit the root cause."],
    }
    result = await graph.ainvoke(
        inputs,
        config={"callbacks": [FileLoggerHandler()]},
    )
    print("Final submission result:", result)


if __name__ == "__main__":
    asyncio.run(run_submission_agent())
