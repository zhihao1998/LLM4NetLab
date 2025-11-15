import os


class MCPServerConfig:
    def __init__(
        self,
        session_id: str,
        root_cause_category: str,
        root_cause_type: str,
        task_level: str,
        lab_name: str,
        backend_model_name: str,
        agent_name: str = "ReAct",
    ):
        # load paths
        base_dir = os.getenv("BASE_DIR")
        self.mcp_server_dir = os.path.join(base_dir, "src/llm4netlab/service/mcp_server")
        self.backend_model_name = backend_model_name
        self.agent_name = agent_name
        self.session_id = session_id
        self.task_level = task_level
        self.root_cause_category = root_cause_category
        self.root_cause_type = root_cause_type
        self.lab_name = lab_name

    def load_config(self):
        # Create configuration dictionary
        config = {
            "mcpServers": {
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
                "task_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/task_mcp_server.py"],
                    "transport": "stdio",
                },
            },
        }

        # add env to every server for the submission
        for server in config["mcpServers"].values():
            server["env"] = {
                "LAB_SESSION_ID": self.session_id,
                "ROOT_CAUSE_CATEGORY": self.root_cause_category,
                "ROOT_CAUSE_TYPE": self.root_cause_type,
                "TASK_LEVEL": self.task_level,
                "LAB_NAME": self.lab_name,
                "BACKEND_MODEL_NAME": self.backend_model_name,
                "AGENT_NAME": self.agent_name,
            }
        return config
