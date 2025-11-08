import asyncio
import logging

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.service.mcp_servers import MCPServer

# Load environment variables
load_dotenv()


# define agent
class AgentWithMCP(AgentBase):
    def __init__(self, name, llm, client, max_steps, system_prompt_template=MCP_PROMPT_TEMPLATE):
        super().__init__()
        self.name = name
        self.agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=max_steps,
            system_prompt_template=system_prompt_template,
        )

    async def arun(self, query: str) -> str:
        """
        Asynchronous run method to process a query.
        """
        return await self.agent.run(query)


async def main():
    # 1. Initialize orchestrator and problem
    orchestrator = Orchestrator()
    task_desc, session_id, problem_id, lab_name = orchestrator.init_problem("frr_down_detection")
    # 2. Load MCP server and client
    mcp_server_config = MCPServer().load_config(session_id=session_id, problem_id=problem_id, lab_name=lab_name)
    client = MCPClient.from_dict(mcp_server_config)
    # 4. Create and register Agent
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    agent = AgentWithMCP(name="MCPAgent_DeepSeek", llm=llm, client=client, max_steps=20)
    orchestrator.register_agent(agent, agent.name)
    # 5. Ready? Go!
    result = await agent.arun(task_desc)
    print("\n\nFinal Result:", result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
