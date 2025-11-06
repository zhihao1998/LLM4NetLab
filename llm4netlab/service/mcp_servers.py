import os


class MCPServer:
    def __init__(self):
        # load paths
        base_dir = os.getenv("BASE_DIR")
        assert base_dir is not None, "BASE_DIR environment variable is not set."
        self.mcp_server_dir = os.path.join(base_dir, "llm4netlab/service/mcp_server")

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
                "AGENT_NAME": "MCPAgent_DeepSeek",
            }
        return config
