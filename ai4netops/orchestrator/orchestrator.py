import time

from ai4netops.net_env.mininet.mininet_env import MininetEnv
from ai4netops.service.bmv2_thrift_api import Bmv2ThriftAPI
from ai4netops.service.mininet_api import MininetAPI
from ai4netops.utils.error_utils import InvalidActionError, ResponseParsingError
from ai4netops.utils.session import Session

"""Orchestrator class that interfaces with the agent and the environment."""


class Orchestrator:
    def __init__(self):
        self.agent = None
        self.session = None

        self.net_env = MininetEnv()

        self.bmv2_thrift_api = Bmv2ThriftAPI()
        self.mininet_api = MininetAPI()

        self.orchestration_start_time = None
        self.orchestration_end_time = None

    def init_problem(self, problem_id: str) -> tuple:
        """Initialize the problem to solve.

        Args:
            problem_id: The problem ID.

        Returns:
            Tuple of problem description, instructions, and APIs.
        """
        self.orchestration_start_time = time.time()

        self.session = Session()
        print("Initializing session...")
        print(f"Session ID: {self.session.session_id}")
        self.session.set_problem(problem_id)

        # Initialize the network environment
        self.init_net_env()

        # Get the problem description, instructions, and APIs
        problem_desc, instructions, apis = self.session.problem.get_problem_info()
        self.session.set_problem(problem_desc)
        self.session.set_agent("react")

        return problem_desc, instructions, apis

    def init_net_env(self, problem_id: str) -> None:
        pass

    def register_agent(self, agent, agent_name) -> None:
        """Register an agent with the orchestrator.

        Args:
            agent: The agent to register.
            agent_name: The name of the agent.
        """
        self.agent = agent
        self.agent_name = agent_name

    async def ask_agent(self, input: str) -> str:
        """Ask the agent the next step given the current context.

        Args:
           input: The input to the agent.

        Returns:
            The agent's response.
        """
        assert self.agent is not None, "Agent not registered"
        assert self.session is not None, "Session not initialized"

        agent_response = await self.agent.get_action(input=input)
        self.session.add(
            {
                "role": "assistant",
                "content": agent_response,
            }
        )
        return agent_response

    async def ask_env(self, input):
        """Ask the environment for the observation given the current action."""
        assert self.session is not None

        try:
            resp = self.parser.parse(input)
        except ResponseParsingError as e:
            self.session.add({"role": "env", "content": str(e)})
            return str(e)

        api, args, kwargs = resp["api_name"], resp["args"], resp["kwargs"]

        # if submit, save solution for eval
        if api == "submit":
            self.session.set_solution(args[0] if len(args) == 1 else args)

        try:
            env_response = self.session.problem.perform_action(api, *args, **kwargs)
        except InvalidActionError as e:
            env_response = str(e)

        self.session.add({"role": "env", "content": env_response})

        return env_response


if __name__ == "__main__":
    orchestrator = Orchestrator()
    # orchestrator.register_agent(agent, name="react")
    # orchestrator.init_problem("pid")
    # orchestrator.ask_agent("input")
    # orchestrator.ask_env("input")
