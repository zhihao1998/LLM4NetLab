import asyncio
import logging

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import Field
from typing_extensions import TypedDict

from agent.domain_agents.diagnosis_agent import DiagnosisAgent
from agent.domain_agents.submission_agent import SubmissionAgent
from agent.utils.loggers import FileLoggerHandler

load_dotenv()


logging.basicConfig(level=logging.INFO)


class AgentState(TypedDict):
    """The state of the agent."""

    messages: list[BaseMessage]
    diagnosis_result: str = Field(
        default="",
        description="The diagnosis result of the network issue.",
    )


class BasicReActAgent:
    def __init__(self, backend_model, max_steps: int = 20):
        self.max_steps = max_steps
        # load agent and tools
        diagnosis_agent = DiagnosisAgent(backend_model=backend_model)
        asyncio.run(diagnosis_agent.load_tools())
        self.diagnosis_agent = diagnosis_agent.get_agent()

        submission_agent = SubmissionAgent(backend_model=backend_model)
        asyncio.run(submission_agent.load_tools())
        self.submission_agent = submission_agent.get_agent()

        # build the state graph
        worker_builder = StateGraph(AgentState)
        worker_builder.add_node("diagnosis_agent", self.diagnosis_agent_builder)
        worker_builder.add_node("submission_agent", self.submission_agent_builder)

        worker_builder.add_edge(START, "diagnosis_agent")
        worker_builder.add_edge("diagnosis_agent", "submission_agent")
        worker_builder.add_edge("submission_agent", END)

        # compile the graph
        self.graph = worker_builder.compile()

    async def run(self, task_description: dict):
        result = await self.graph.ainvoke(
            {"messages": [HumanMessage(content=task_description)]},
            config={"callbacks": [FileLoggerHandler()], "max_steps": self.max_steps},
        )
        return result

    async def diagnosis_agent_builder(self, state: AgentState):
        diagnosis_result = await self.diagnosis_agent.ainvoke(
            {"messages": state["messages"]},
            config={"callbacks": [FileLoggerHandler()], "max_steps": self.max_steps},
            debug=True,
        )
        return {"diagnosis_result": [diagnosis_result["messages"][-1].content]}

    async def submission_agent_builder(self, state: AgentState):
        result = await self.submission_agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"Based on the diagnosis result: {state['diagnosis_result']}, please provide the submission."
                    )
                ]
            },
            config={"callbacks": [FileLoggerHandler()], "max_steps": self.max_steps},
            debug=True,
        )
        return result
