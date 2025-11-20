import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import Field
from typing_extensions import TypedDict

import llm4netlab.net_env.kathara as NetEnvKathara
from agent.domain_agents.diagnosis_agent import DiagnosisAgent
from agent.domain_agents.submission_agent import SubmissionAgent
from agent.utils.loggers import FileLoggerHandler
from llm4netlab.config import RESULTS_DIR
from llm4netlab.orchestrator.orchestrator import Orchestrator
from llm4netlab.utils.session import SessionKey

load_dotenv()


logging.basicConfig(level=logging.INFO)


class AgentState(TypedDict):
    """The state of the agent."""

    diagnosis_result: str = Field(
        default="",
        description="The diagnosis result of the network issue.",
    )


"""
Initialize the network scenario and inject failure
"""
backend_model_name = "gpt-oss:20b"
root_cause_name = "frr_service_down"
task_level = "localization"
net_env = NetEnvKathara.DCClosBGP()
agent_name = "ReAct"

orchestrator = Orchestrator()
root_cause_category, task_desc, session_id, lab_name = orchestrator.init_problem(
    root_cause_name=root_cause_name,
    task_level=task_level,
    net_env=net_env,
    agent_name=agent_name,
    backend_model_name=backend_model_name,
)

session_key = SessionKey(
    lab_name=lab_name,
    session_id=session_id,
    root_cause_category=root_cause_category,
    root_cause_name=root_cause_name,
    task_level=task_level,
    backend_model_name=backend_model_name,
    agent_name=agent_name,
)

log_path = os.path.join(
    f"{RESULTS_DIR}/{session_key.root_cause_category}/{session_key.root_cause_name}/{session_key.task_level}/"
    f"{session_key.session_id}_{session_key.backend_model_name}_conversation.log"
)

"""
Generate the task description as the input to the agent
"""
inputs = {
    "messages": [task_desc],
}

"""
Initialize two agents and load MCP tools: DiagnosisAgent and SubmissionAgent.

This seperation is to prevent data leakage during the diagnosis process, since the SubmissionAgent is allowed to access the ground truth information.
"""
submission_agent = SubmissionAgent(session_key)
asyncio.run(submission_agent.load_tools())
submission_agent = submission_agent.get_agent()

diagnosis_agent = DiagnosisAgent(session_key)
asyncio.run(diagnosis_agent.load_tools())
diagnosis_agent = diagnosis_agent.get_agent()

"""
Define the graph nodes
"""


async def diagnosis_agent_builder(state: AgentState):
    diagnosis_result = await diagnosis_agent.ainvoke(
        inputs, config={"callbacks": [FileLoggerHandler(log_path=log_path)]}, debug=True
    )
    return {"diagnosis_result": [diagnosis_result["messages"][-1].content]}


async def submission_agent_builder(state: AgentState):
    result = await submission_agent.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=f"Based on the diagnosis result: {state['diagnosis_result']}, please provide the submission."
                )
            ]
        },
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
        debug=True,
    )
    return result


"""
Define the signle direction graph between the two agents
"""
worker_builder = StateGraph(AgentState)

worker_builder.add_node("diagnosis_agent", diagnosis_agent_builder)
worker_builder.add_node("submission_agent", submission_agent_builder)

worker_builder.add_edge(START, "diagnosis_agent")
worker_builder.add_edge("diagnosis_agent", "submission_agent")
worker_builder.add_edge("submission_agent", END)


"""
Compile and run the agent graph.
"""


async def run_agent_graph():
    final_agent = worker_builder.compile()
    result = await final_agent.ainvoke(
        {},
        config={"callbacks": [FileLoggerHandler(log_path=log_path)]},
        debug=True,
    )
    print("Final result:", result)
    orchestrator.stop_problem(cleanup=False)

    orchestrator.eval_problem()


if __name__ == "__main__":
    asyncio.run(run_agent_graph())
