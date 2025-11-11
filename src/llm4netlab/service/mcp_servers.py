import os


class MCPServer:
    def __init__(self, model_name: str = None):
        # load paths
        base_dir = os.getenv("BASE_DIR")
        assert base_dir is not None, "BASE_DIR environment variable is not set."
        self.mcp_server_dir = os.path.join(base_dir, "src/llm4netlab/service/mcp_server")
        self.model_name = model_name

    def load_config(self, session_id: str, problem_id: str, lab_name: str):
        # Create configuration dictionary
        config = {
            "mcpServers": {
                "kathara_base_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_base_mcp_server.py"],
                },
                "generic_tools_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/generic_tools_mcp_server.py"],
                },
                "kathara_frr_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/kathara_frr_mcp_server.py"],
                },
                "task_mcp_server": {
                    "command": "python3",
                    "args": [f"{self.mcp_server_dir}/task_mcp_server.py"],
                },
            },
        }

        # add env to every server
        for server in config["mcpServers"].values():
            server["env"] = {
                "LAB_SESSION_ID": session_id,
                "LAB_PROBLEM_ID": problem_id,
                "LAB_NAME": lab_name,
                "MODEL_NAME": self.model_name or "MCPAgent",
            }
        return config
