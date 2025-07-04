import inspect
import time

from llm4netlab.orchestrator.problems.prob_pool import get_problem_instance
from llm4netlab.utils.errors import InvalidActionError, ResponseParsingError, SessionPrint
from llm4netlab.utils.parser import ResponseParser
from llm4netlab.utils.session import Session
from llm4netlab.utils.submission import SubmissionStatus

"""Orchestrator class that interfaces with the agent and the environment."""


class Orchestrator:
    def __init__(self):
        self.agent = None
        self.session = None
        self.session_print = SessionPrint()
        self.problem = None
        self.parser = ResponseParser()

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

        self.problem = get_problem_instance(problem_id)
        self.session.set_problem(self.problem, problem_id)
        self.session.set_agent(self.agent_name)

        # deploy the network environment
        # check if the environment is already deployed
        if not self.problem.net_env.lab_exists():
            print("Deploying network environment...")
            self.problem.net_env.deploy()

        self.problem.inject_fault()

        # Get the problem description, instructions, and APIs
        task_desc = self.problem.get_task_description()
        instructions = self.problem.get_instructions()
        actions = self.problem.get_available_actions()
        return task_desc, instructions, actions

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
            result = self.session.problem.perform_action(api, *args, **kwargs)

            if inspect.iscoroutine(result):
                env_response = await result
            else:
                env_response = result

        except InvalidActionError as e:
            env_response = str(e)

        self.session.add({"role": "env", "content": env_response})
        return env_response

    async def start_problem(self, max_steps=10):
        """Start the problem."""
        assert self.session is not None, "Session not initialized"
        action_instr = "Please take the next action"
        action, env_response, results = "", "", {}
        self.session.start()

        for step in range(max_steps):
            action = await self.ask_agent(action_instr)
            self.session_print.agent(action)
            # action = (
            #     '```\n bmv2_show_tables("simple_bmv2", "s3") \n```'  # For testing purposes, replace with agent response
            # )
            env_response = await self.ask_env(action)
            self.session_print.service(env_response)

            if env_response == SubmissionStatus.VALID_SUBMISSION:
                break
            elif env_response == SubmissionStatus.INVALID_SUBMISSION:
                raise ValueError("Invalid submission!")

            action_instr = env_response + "\n" + "Please take the next action"

        self.session.end()

    def stop_problem(self, cleanup=False):
        """Stop the problem."""
        assert self.session is not None, "Session not initialized"
        assert self.problem is not None, "Problem not initialized"

        self.orchestration_end_time = time.time()
        if cleanup:
            self.problem.net_env.undeploy()
            print(f"Network environment {self.problem.net_env.name} undeployed.")
