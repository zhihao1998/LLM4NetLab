import os

from llm4netlab.utils.session import Session


class MCPServerConfig:
    def __init__(self):
        # load paths
        base_dir = os.getenv("BASE_DIR")
        self.mcp_server_dir = os.path.join(base_dir, "src/llm4netlab/service/mcp_server")
        self.session = Session()
        self.session.load_running_session()

    def load_config(self, if_submit: bool = False) -> dict:
        if if_submit:
            config = {
                "task_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/task_mcp_server.py"],
                    "transport": "stdio",
                },
            }
        else:
            config = {
                "kathara_base_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_base_mcp_server.py"],
                    "transport": "stdio",
                },
                "kathara_frr_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_frr_mcp_server.py"],
                    "transport": "stdio",
                },
                "kathara_bmv2_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_bmv2_mcp_server.py"],
                    "transport": "stdio",
                },
                "kathara_telemetry_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_telemetry_mcp_server.py"],
                    "transport": "stdio",
                },
            }

        # add env to every server for the submission
        for server in config.values():
            server["env"] = {
                "LAB_SESSION_ID": self.session.session_id,
                "root_cause_name": self.session.root_cause_name,
                "LAB_NAME": self.session.scenario_name,
                "backend_model": self.session.backend_model,
                "agent_type": self.session.agent_type,
            }
        return config
