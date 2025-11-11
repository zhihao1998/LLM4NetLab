import asyncio
import logging
import os

from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from agent.llm.langchain_ollama import OllamaLLM
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.service.mcp_servers import MCPServer
from llm4netlab.utils.loggers import FileLoggerHandler

# Load environment variables
load_dotenv()
RESULTS_DIR = os.getenv("RESULTS_DIR")


# define agent
class AgentWithMCP(AgentBase):
    def __init__(self, name, llm, client, max_steps, log_path, system_prompt_template=MCP_PROMPT_TEMPLATE):
        super().__init__()
        self.name = name
        self.agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=max_steps,
            system_prompt_template=system_prompt_template,
            callbacks=[FileLoggerHandler(log_path=log_path)],
        )

    async def arun(self, query: str) -> str:
        """
        Asynchronous run method to process a query.
        """
        return await self.agent.run(query)


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    model = "gpt-oss:20b"
    task_desc, session_id, problem_id, lab_name = orchestrator.init_problem("frr_down_localization")
    # 2. Load MCP server and client
    mcp_server_config = MCPServer(model_name=model).load_config(
        session_id=session_id, problem_id=problem_id, lab_name=lab_name
    )
    # 3. Create MCP client
    client = MCPClient.from_dict(mcp_server_config)

    # 4. Create and register Agent
    llm = OllamaLLM(model=model)

    log_path = os.path.join(f"{RESULTS_DIR}/{problem_id}/{session_id}_conversation.log")
    agent = AgentWithMCP(name="MCPAgent_Ollama", llm=llm, client=client, max_steps=20, log_path=log_path)
    orchestrator.register_agent(agent, agent.name)
    # 5. Ready? Go!
    result = await agent.arun(task_desc)
    print("\n\nFinal Result:", result)

    orchestrator.stop_problem(cleanup=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
