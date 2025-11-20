import os

from llm4netlab.utils.session import SessionKey


class MCPServerConfig:
    def __init__(
        self,
        session_key: SessionKey,
    ):
        # load paths
        base_dir = os.getenv("BASE_DIR")
        self.mcp_server_dir = os.path.join(base_dir, "src/llm4netlab/service/mcp_server")
        self.backend_model_name = session_key.backend_model_name
        self.agent_name = session_key.agent_name
        self.session_id = session_key.session_id
        self.task_level = session_key.task_level
        self.root_cause_category = session_key.root_cause_category
        self.root_cause_name = session_key.root_cause_name
        self.lab_name = session_key.lab_name

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
                "generic_tools_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/generic_tools_mcp_server.py"],
                    "transport": "stdio",
                },
                "kathara_frr_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_frr_mcp_server.py"],
                    "transport": "stdio",
                },
            }

        # add env to every server for the submission
        for server in config.values():
            server["env"] = {
                "LAB_SESSION_ID": self.session_id,
                "ROOT_CAUSE_CATEGORY": self.root_cause_category,
                "ROOT_CAUSE_NAME": self.root_cause_name,
                "TASK_LEVEL": self.task_level,
                "LAB_NAME": self.lab_name,
                "BACKEND_MODEL_NAME": self.backend_model_name,
                "AGENT_NAME": self.agent_name,
            }
        return config
