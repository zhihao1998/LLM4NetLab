import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.llm.model_factory import load_ollama_model
from agent.utils.loggers import FileLoggerHandler
from agent.utils.mcp_servers import MCPServerConfig
from agent.utils.template import OVERALL_DIAGNOSIS_PROMPT
from llm4netlab.config import RESULTS_DIR
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.utils.session import SessionKey

load_dotenv()


class DiagnosisAgent:
    """An agent that performs the total process of network diagnosis using the ReAct framework."""

    def __init__(self, backend_model: str = "gpt-oss:20b"):
        mcp_server_config = MCPServerConfig().load_config(if_submit=False)
        self.client = MultiServerMCPClient(connections=mcp_server_config)
        self.tools = None
        self.llm = load_ollama_model(backend_model=backend_model)

    async def load_tools(self):
        self.tools = await self.client.get_tools()

    def get_agent(self):
        agent = create_agent(
            model=self.llm,
            system_prompt=OVERALL_DIAGNOSIS_PROMPT,
            tools=self.tools,
        )
        return agent


async def run_diagnosis_agent():
    logging.basicConfig(level=logging.INFO)
    backend_model = "gpt-oss:20b"
    orchestrator = Orchestrator()
    root_cause_name = "frr_service_down"
    task_level = "rca"

    root_cause_category, task_desc, session_id, lab_name = orchestrator.init_problem(
        root_cause_name=root_cause_name, task_level=task_level
    )

    session_key = SessionKey(
        lab_name=lab_name,
        session_id=session_id,
        root_cause_category=root_cause_category,
        root_cause_name=root_cause_name,
        task_level=task_level,
        backend_model=backend_model,
        agent_type="DiagnosisAgent",
    )
    submission_agent = DiagnosisAgent(session_key)
    await submission_agent.load_tools()

    log_path = os.path.join(
        f"{RESULTS_DIR}/{session_key.root_cause_category}/{session_key.root_cause_name}/{session_key.task_level}/"
        f"{session_key.session_id}_{session_key.backend_model}_conversation.log"
    )

    graph = submission_agent.get_agent()
    inputs = {
        "messages": [task_desc],
    }
    result = await graph.ainvoke(
        inputs,
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
    )
    print("Final result:", result)


if __name__ == "__main__":
    asyncio.run(run_diagnosis_agent())
