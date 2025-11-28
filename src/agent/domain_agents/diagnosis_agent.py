import asyncio
import logging

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools.structured import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.llm.model_factory import load_model
from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig
from llm4netlab.orchestrator.orchestrator import Orchestrator

load_dotenv()

OVERALL_DIAGNOSIS_PROMPT = """\
    You are a network troubleshooting expert.
    Focus on (1) detecting if there is an anomaly, (2) localizing the faulty devices, and (3) identifying the root cause.
    
    Basic requirements:
    - Use the provided tools to gather necessary information.
    - Do not provide mitigation unless explicitly required.
"""


class DiagnosisAgent:
    """An agent that performs the total process of network diagnosis using the ReAct framework."""

    def __init__(self, backend_model: str = "gpt-oss:20b"):
        mcp_server_config = MCPServerConfig().load_config(if_submit=False)
        self.client = MultiServerMCPClient(connections=mcp_server_config)
        self.tools = None
        self.llm = load_model(backend_model=backend_model)

    async def load_tools(self):
        self.tools: list[StructuredTool] = await self.client.get_tools()
        for tool in self.tools:
            tool.handle_tool_error = True
            tool.handle_validation_error = True

    def get_agent(self):
        agent = create_agent(
            model=self.llm, system_prompt=OVERALL_DIAGNOSIS_PROMPT, tools=self.tools, name="DiagnosisAgent"
        )
        return agent


async def run_diagnosis_agent():
    logging.basicConfig(level=logging.INFO)
    orchestrator = Orchestrator()
    root_cause_name = "frr_service_down"
    task_level = "rca"

    root_cause_category, task_desc, session_id, lab_name = orchestrator.init_problem(
        root_cause_name=root_cause_name, task_level=task_level
    )

    submission_agent = DiagnosisAgent()
    await submission_agent.load_tools()

    graph = submission_agent.get_agent()
    inputs = {
        "messages": [task_desc],
    }
    result = await graph.ainvoke(
        inputs,
        config={"callbacks": [FileLoggerHandler()]},
    )
    print("Final result:", result)


if __name__ == "__main__":
    asyncio.run(run_diagnosis_agent())
