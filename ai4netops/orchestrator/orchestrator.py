from ai4netops.tools.bmv2_thrift_api import Bmv2ThriftAPI
from ai4netops.tools.mininet_api import MininetAPI

"""Orchestrator class that interfaces with the agent and the environment."""


class Orchestrator:
    def __init__(self):
        self.bmv2_thrift_api = Bmv2ThriftAPI()
        self.mininet_api = MininetAPI()

    def init_net_env(self):
        pass

    def register_agent(self, agent, agent_name):
        self.agent = agent
        self.agent_name = agent_name
