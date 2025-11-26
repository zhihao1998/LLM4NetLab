import argparse
import asyncio
import logging

from agent.react_agent import BasicReActAgent
from llm4netlab.utils.session import Session


def _agent_selector(agent_type: str, backend_model: str, max_steps: int = 20):
    match agent_type.lower():
        case "react":
            return BasicReActAgent(backend_model=backend_model, max_steps=max_steps)
        case _:
            pass


def start_agent(agent_type: str, backend_model: str, max_steps: int):
    logger = logging.getLogger("AgentRunner")

    session = Session()
    session.load_running_session()
    session.update_session("agent_type", agent_type)
    session.update_session("backend_model", backend_model)
    session.start_session()

    logger.info(f"Starting agent: {agent_type}  with backend {backend_model} in session {session.session_id}")
    agent = _agent_selector(agent_type, backend_model, max_steps=max_steps)
    asyncio.run(agent.run(task_description=session.task_description))

    # stop session
    session.end_session()
    logger.info(f"Agent run completed for session ID: {session.session_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Inject Failure into Network Environment")
    parser.add_argument(
        "--agent_type", type=str, nargs="?", default="ReAct", help="Type of agent to run (default: ReAct)"
    )
    parser.add_argument(
        "--backend_model",
        type=str,
        nargs="?",
        default="gpt-oss:20b",
        help="Backend model for the agent (default: gpt-oss:20b)",
    )
    parser.add_argument(
        "--max_steps", type=int, nargs="?", default=20, help="Maximum steps for the agent to take (default: 20)"
    )
    args = parser.parse_args()
    start_agent(args.agent_type, args.backend_model, args.max_steps)
