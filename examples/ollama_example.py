import asyncio
import logging
import os

from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from agent.llm.langchain_ollama import OllamaLLM
from agent.utils.loggers import FileLoggerHandler
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.config import RESULTS_DIR
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.service.mcp_servers import MCPServer


# define agent
class AgentWithMCP(AgentBase):
    def __init__(
        self, agent_name, backend_model, llm, client, max_steps, log_path, system_prompt_template=MCP_PROMPT_TEMPLATE
    ):
        super().__init__()
        self.agent_name = agent_name
        self.backend_model = backend_model
        self.callback_handler = FileLoggerHandler(log_path=log_path)
        self.agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=max_steps,
            system_prompt_template=system_prompt_template,
            callbacks=[self.callback_handler],
        )

    async def arun(self, query: str) -> str:
        """
        Asynchronous run method to process a query.
        """
        return await self.agent.run(query)


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    # model_name = "qwen3:32b"
    model_name = "gpt-oss:20b"

    task_desc, session_id, problem_id, lab_name = orchestrator.init_problem("frr_down_localization")
    # 2. Load MCP server and client
    mcp_server_config = MCPServer(model_name=model_name).load_config(
        session_id=session_id, problem_id=problem_id, lab_name=lab_name
    )
    # 3. Create MCP client
    client = MCPClient.from_dict(mcp_server_config)

    # 4. Create and register Agent
    llm = OllamaLLM(model=model_name)

    log_path = os.path.join(f"{RESULTS_DIR}/{problem_id}/{session_id}_{model_name}_conversation.log")
    agent = AgentWithMCP(
        agent_name=f"ReAct_Ollama_{model_name}",
        backend_model=model_name,
        llm=llm,
        client=client,
        max_steps=20,
        log_path=log_path,
    )
    orchestrator.register_agent(agent)
    # 5. Ready? Go!
    result = await agent.arun(task_desc)
    print("\n\nFinal Result:", result)

    orchestrator.eval()

    orchestrator.stop_problem(cleanup=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
