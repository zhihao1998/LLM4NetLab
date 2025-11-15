import asyncio
import logging
import os
from textwrap import dedent

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.llm.model_factory import load_default_model
from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig

load_dotenv()
RESULTS_DIR = os.getenv("RESULTS_DIR")

SUBMIT_PROMPT_TEMPLATE = dedent("""\
    You are an expert network engineer.
    Your task is to submit the final solution for this network problem.
    You can use the tools to submit your solution.
""").strip()


class TaskAgent:
    def __init__(self, backend_model_name: str, agent_name: str, session_id: str, root_cause_type: str, lab_name: str):
        self.backend_model_name = backend_model_name
        self.agent_name = agent_name
        self.session_id = session_id
        self.root_cause_type = root_cause_type
        self.lab_name = lab_name

        # load submission tools
        mcp_server_config = MCPServerConfig(
            backend_model_name=backend_model_name,
            session_id=session_id,
            root_cause_type=root_cause_type,
            lab_name=lab_name,
        ).load_config()["mcpServers"]["task_mcp_server"]

        self.client = MultiServerMCPClient(connections={"task_mcp_server": mcp_server_config})

        self.tools = None

        self.llm = load_default_model()

    async def load_tools(self):
        self.tools = await self.client.get_tools()

    def get_task_agent(self):
        """Final submission node"""
        agent = create_agent(
            model=self.llm,
            system_prompt=SUBMIT_PROMPT_TEMPLATE,
            tools=self.tools,
        )
        return agent


async def run_task_agent():
    logging.basicConfig(level=logging.INFO)
    task_agent = TaskAgent(
        backend_model_name="gpt-oss:20b",
        agent_name="TaskAgent",
        session_id="example_session_id",
        root_cause_type="host_ip_missing_detection",
        lab_name="test_lab",
    )
    await task_agent.load_tools()

    log_path = os.path.join(
        f"{RESULTS_DIR}/{task_agent.root_cause_type}/{task_agent.session_id}_{task_agent.backend_model_name}_conversation.log"
    )

    graph = task_agent.get_task_agent()
    inputs = {
        "messages": ["There is a host IP missing problem at host pc_0_0."],
        "llm_calls": 0,
    }
    result = await graph.ainvoke(
        inputs,
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
    )
    print("Final submission result:", result)


if __name__ == "__main__":
    asyncio.run(run_task_agent())
