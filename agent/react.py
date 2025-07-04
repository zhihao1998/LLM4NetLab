"""Naive ReAct client for LLM4NetLab.
Reproduce from the AI4NetOps.

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022).
React: Synergizing reasoning and acting in language models. arXiv preprint arXiv:2210.03629.

Code: https://github.com/ysymyth/ReAct
Paper: https://arxiv.org/abs/2210.03629
"""

import asyncio

from agent.base import AgentBase
from agent.llm import LLMBase
from llm4netlab.orchestrator.orchestrator import Orchestrator


class ReactAgent(AgentBase):
    def __init__(self):
        self.history = []
        self.llm = LLMBase()


if __name__ == "__main__":
    orchestrator = Orchestrator()
    agent = ReactAgent()
    orchestrator.register_agent(agent, "react")

    task_desc, instructions, actions = orchestrator.init_problem("packet_loss_detection")
    print("Task description:", task_desc)
    print("Instructions:", instructions)
    print("Actions:", actions)

    agent.init_context(task_desc, instructions, actions)
    print("Agent context initialized.")

    asyncio.run(orchestrator.start_problem(max_steps=30))

    orchestrator.stop_problem()
