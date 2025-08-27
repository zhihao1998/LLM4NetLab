import asyncio
import logging

import dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


async def main():
    client = MultiServerMCPClient(
        {
            "kathara_base_mcp_server": {
                "command": "python3",
                "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_base_mcp_server.py"],
                "transport": "stdio",
            },
            "kathara_bmv2_mcp_server": {
                "command": "python3",
                "args": ["/home/p4/codes/AI4NetOps/llm4netlab/service/mcp_server/kathara_bmv2_mcp_server.py"],
                "transport": "stdio",
            },
        }
    )
    tools = await client.get_tools()
    agent = create_react_agent(
        "deepseek-reasoner",  # or any other LLM you have access to
        tools,
    )
    math_response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "(1) report the current reachability of the network; "
                    "(2) check the state of bmv2 switch `s1` in `simple_bmv2` network environment; "
                    "(3) check if there is any counters of bmv2 switch `s2` in `simple_bmv2` network environment",
                }
            ]
        }
    )

    print(math_response)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dotenv.load_dotenv("/home/p4/codes/AI4NetOps/.env")
    asyncio.run(main())
