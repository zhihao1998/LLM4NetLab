import asyncio
import logging
import os
from textwrap import dedent

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools.structured import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.llm.model_factory import load_model
from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig
from llm4netlab.config import RESULTS_DIR
from llm4netlab.utils.session import SessionKey

load_dotenv()

SUBMIT_PROMPT_TEMPLATE = dedent("""\
    You are an expert network engineer.
    Your task is to submit the final solution for this network problem based on the diagnosis results provided.
    Carefully review the diagnosis results and ensure that your submission is accurate and complete.
    Provide your final answer in the required format.
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
            model=self.llm,
            system_prompt=SUBMIT_PROMPT_TEMPLATE,
            tools=self.tools,
        )
        return agent


async def run_submission_agent():
    logging.basicConfig(level=logging.INFO)
    session_key = SessionKey(
        lab_name="test_lab",
        session_id="example_session_id",
        root_cause_category="device_failure",
        root_cause_name="frr_service_down",
        task_level="detection",
        backend_model="gpt-oss:20b",
        agent_type="SubmissionAgent",
    )
    submission_agent = SubmissionAgent(session_key)
    await submission_agent.load_tools()

    log_path = os.path.join(
        f"{RESULTS_DIR}/{session_key.root_cause_category}/{session_key.root_cause_name}/{session_key.task_level}/"
        f"{session_key.session_id}_{session_key.backend_model}_conversation.log"
    )

    graph = submission_agent.get_agent()
    inputs = {
        "messages": ["There is a failed FRR service on router1. Please submit the root cause."],
    }
    result = await graph.ainvoke(
        inputs,
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
    )
    print("Final submission result:", result)


if __name__ == "__main__":
    asyncio.run(run_submission_agent())
