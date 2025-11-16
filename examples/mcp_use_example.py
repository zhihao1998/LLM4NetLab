import asyncio
import logging

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from mcp_use import MCPAgent, MCPClient

from agent.base import AgentBase
from agent.utils.mcp_servers import MCPServerConfig
from agent.utils.template import MCP_PROMPT_TEMPLATE
from llm4netlab.orchestrator.orchestrator import Orchestrator

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
    task_desc, session_id, root_cause_name, lab_name = orchestrator.init_problem("frr_down_detection")
    # 2. Load MCP server and client
    mcp_server_config = MCPServerConfig().load_config(
        session_id=session_id, root_cause_name=root_cause_name, lab_name=lab_name
    )
    # 3. Create MCP client
    client = MCPClient.from_dict(mcp_server_config)

    # 4. Create and register Agent
    llm = ChatDeepSeek(model="deepseek-reasoner")
    agent = AgentWithMCP(name="MCPAgent_DeepSeek", llm=llm, client=client, max_steps=20)
    orchestrator.register_agent(agent, agent.name)
    # 5. Ready? Go!
    result = await agent.arun(task_desc)
    print("\n\nFinal Result:", result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
