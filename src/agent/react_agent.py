import asyncio
import logging

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from pydantic import Field, ValidationError
from typing_extensions import TypedDict

from agent.domain_agents.diagnosis_agent import DiagnosisAgent
from agent.domain_agents.submission_agent import SubmissionAgent
from agent.utils.loggers import FileLoggerHandler

load_dotenv()


logging.basicConfig(level=logging.INFO)


class AgentState(TypedDict):
    """The state of the agent."""

    messages: list[BaseMessage]
    diagnosis_report: str = Field(
        default="",
        description="The diagnosis report of the network state after analysis.",
    )
    is_max_steps_reached: bool = Field(
        default=False,
        description="Indicates whether the agent has reached the maximum number of steps allowed.",
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
        worker_builder.add_conditional_edges(
            "diagnosis_agent",
            lambda state: state.get("is_max_steps_reached", False),
            {
                True: END,
                False: "submission_agent",
            },
        )

        worker_builder.add_edge("submission_agent", END)

        # compile the graph
        self.graph = worker_builder.compile()

    async def run(self, task_description: str):
        result = await self.graph.ainvoke(
            {"messages": [HumanMessage(content=task_description)]},
        )
        return result

    async def diagnosis_agent_builder(self, state: AgentState):
        try:
            diagnosis_report = await self.diagnosis_agent.ainvoke(
                {"messages": state["messages"]},
                config={
                    "callbacks": [FileLoggerHandler(name="diagnosis_agent")],
                    "recursion_limit": self.max_steps,
                },
                debug=True,
            )
            return {"diagnosis_report": [diagnosis_report["messages"][-1].content], "is_max_steps_reached": False}
        except ValidationError as e:
            return {"diagnosis_report": [f"Error: diagnosis agent failed with validation error: {str(e)}"]}
        except GraphRecursionError:
            return {
                "messages": [HumanMessage(content="Error: diagnosis did not finish within max steps.")],
                "diagnosis_report": ["ERROR_MAX_STEPS_REACHED"],
                "is_max_steps_reached": True,
            }

    async def submission_agent_builder(self, state: AgentState):
        diag_text = state["diagnosis_report"][-1]
        result = await self.submission_agent.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"Based on the diagnosis report: {diag_text}, please provide the submission. Do not submit if no report available."
                    ),
                ]
            },
            config={
                "callbacks": [FileLoggerHandler(name="submission_agent")],
                "recursion_limit": self.max_steps,
            },
            debug=True,
        )
        return {
            "messages": result["messages"],
        }
