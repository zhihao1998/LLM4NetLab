<div align="center">
<h1>LLM4NetLab</h1>

[🤖Overview](#🤖overview) | 
[📦Installation](#📦installation) | 
[🚀Quick Start](#🚀quick-start) | 
[🛠️Usage](#🛠️usage) | 
[📚Cite](#📚cite)

[![ArXiv Link](https://img.shields.io/badge/arXiv-2507.01997-red?logo=arxiv)](https://arxiv.org/abs/2507.01997v1) [![NGNO'25 Proceedings](https://img.shields.io/badge/NGNO'25%20Proceedings-blue)](https://dl.acm.org/doi/10.1145/3748496.3748990)

</div>

<h1 id="🤖overview">🤖 Overview</h1>

![alt text](./assets/images/llm4netlab_architecture.png)

LLM4NetLab is a standardized, reproducible, and open benchmarking platform to build and evaluate AI agents on network troubleshooting with low operational effort. This platform primarily aims to *standardize* and *democratize* the experimentation with AI agents, by enabling researchers and practitioners -- including non domain-experts such as ML engineers and data scientists -- to focus on the evaluation of AI agents on curated problem sets, without concern for underlying operational complexities. Custom AI agents can be easily plugged through a single API and rapidly evaluated.

This is the code repository for the paper [Towards a Playground to Democratize Experimentation and Benchmarking of AI Agents for Network Troubleshooting](https://arxiv.org/abs/2507.01997), which was accepted at the [ACM SIGCOMM 2025 1st Workshop on Next-Generation Network Observability (NGNO)](https://conferences.sigcomm.org/sigcomm/2025/workshop/ngno/).

💡 **Note:** We are actively developing LLM4NetLab. If you have any suggestions or are interested in contributing, feel free to reach out to us!

## Features

- Standardized network troubleshooting environment based on Kathará
- [<img src="https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/logo/light.svg?maxW=1338&auto=format&n=4ZXF1PrDkEaJvXpn&q=85&s=f9f25f0b2f8cbf9e7f1f6ac1fc4f1745" alt="MCP" height="16" style="vertical-align:middle;background:white;"> MCP](https://modelcontextprotocol.io/docs/getting-started/intro)-based tool support
- Pre-built network scenarios and fault injection mechanisms
- Reproducible evaluation framework
- Support for various network topologies and configurations
- Easy integration of custom AI agents
- Automatic evaluation mechanism

<h1 id="📦installation">📦 Installation</h1>

## Requirements

- [Kathará](https://www.kathara.org/). 
  Follow the [official installation guide](https://github.com/KatharaFramework/Kathara?tab=readme-ov-file#installation) to install Kathará.
- Python >= 3.12


## Setup

Clone the repository and install the dependencies. 
LLM4NetLab uses [uv](https://docs.astral.sh/uv) to manage the dependencies. Follow [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/) to install uv. You can also use a standard `pip install -e .` to install the dependencies.

```shell
# Clone the repository
git clone https://github.com/zhihao1998/LLM4NetLab.git
cd LLM4NetLab

# Install dependencies
uv sync

# Activate the environment
uv venv activate

# (Optional) Run an interactive shell in the environment
uv run bash
```

The Kathará API relies on Docker to function properly. We recommend to add current user to docker group to avoid calling with `sudo`. **However, please be aware of the security implications of this action.**

```shell
sudo usermod -aG docker $USER
```

Login again or activate temporaily with 

```shell
newgrp docker
```

<h1 id="🚀quick-start">🚀 Quick Start</h1>

## Configure environment variables

Create a `.env` file under the base directory and set the following environment variables:

```shell
BASE_DIR = <your_path_to_this_project>

# if use Langsmith for observability
# check langsmith documentation for more details
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT=<>
LANGSMITH_API_KEY=<>
LANGSMITH_PROJECT=<>

# if use google search MCP server
# check google Programmable Search Engine guides for more details
GOOGLE_SEARCH_API_KEY=<>
GOOGLE_SEARCH_CSE_ID=<>

# api key for you LLM, e.g. DeepSeek-R1 here
DEEPSEEK_API_KEY=<>
```

## Step by step guide
You can follow the steps below to run a complete troubleshooting task with LLM4NetLab.

1. **Start the network environment**
  Check the specific scenario and its parameters under `llm4netlab/net_env`.
   ```shell
   python3 scripts/step1_net_env_start.py --scenario <scenario_name> --scenario_params key1=value1 key2=value2
   ```

2. **Inject faults into the network environment**

   ```shell
   python3 scripts/step2_failure_inject.py --problems <problem_id_1> <problem_id_2> --task_level <detection|localization|rca>
   ```

3. **Run the AI agent to troubleshoot the network**
    ```shell
    python3 scripts/step3_agent_run.py --agent_type <agent_type> --backend_model <backend_model> --max_steps <max_steps>
    ```

4. **Evaluate the agent's performance**

    ```shell
    python3 scripts/step4_result_eval.py --judge_model <judge_model>
    ```


<h1 id="🛠️usage">🛠️ Usage</h1>

## Network Scenarios

LLM4NetLab supports multiple network scenarios under the `llm4netlab/net_env` directory, including data center networks, interdomain routing, intradomain routing, etc. Several supported scenarios based on Kathará include:

- **Interdomain routing** with BGP
- **Intradomain routing** with OSPF
- **Basic P4 L2 forwarding** with BMv2 switches
- **In-band network telemetry (INT) in P4** with BMv2 switches

💡 More scenarios are coming soon!

Each scenario is defined in a Kathará `lab.py` file, which specifies the network topology, devices, and initial configurations. Check [Kathará API Docs](https://github.com/KatharaFramework/Kathara/wiki/Kathara-API-Docs) for more details if you want to create your scenarios.

## Tasks and Problems

Check all available problems at `llm4netlab/orchestrator/problems`. Some of them are listed below.

| Task level   | Issue type                  | Problem ID                       | Description                                           |
| ------------ | --------------------------- | -------------------------------- | ----------------------------------------------------- |
| detection    | device_failure              | frr_down_detection               | Detect if there is a down FRR service.                |
| localization | device_failure              | frr_down_localization            | Localize the failure of FRR service.                  |
| detection    | device_failure              | bmv2_down_detection              | Detect if there is a down BMv2 device.                |
| detection    | config_access_policy_error  | bgp_acl_block_detection          | Detect if ACL blocks BGP traffic.                     |
| detection    | config_routing_policy_error | bgp_asn_misconfig_detection      | Detect ASN misconfiguration causing BGP peer failure. |
| detection    | config_access_policy_error  | ospf_acl_block_detection         | Detect if ACL blocks OSPF traffic.                    |
| detection    | config_routing_policy_error | ospf_misconfig_detection         | Detect OSPF area misconfiguration.                    |
| detection    | p4_runtime_error            | p4_table_entry_missing_detection | Detect missing P4 table entry.                        |
| detection    | performance_degradation     | p4_int_hop_delay_high_detection  | Detect high hop delay in P4 via INT signals.          |
| detection    | performance_degradation     | p4_packet_loss_detection         | Detect packet loss in P4 via port counters .          |

## MCP Servers and Tools

LLM4NetLab provides a set of MCP servers and tools to facilitate network troubleshooting tasks. All servers are available under `src/llm4netlab/service/mcp_server`. These include:

- **base mcp server for Kathará**: This server provides the basic functionality for interacting with Kathará network scenarios, including
  - `get_reachability` to check the reachability by pinging all pairs of hosts.
  - `iperf_test` to run iperf test between any two hosts.
  - `systemctl_ops` to manage system services, i.e., start, stop, restart, status.
  - `get_host_net_config` to retrieve the network configuration of a specific host.
  - `nft_list_ruleset` to get the current nftables ruleset.
- **BMv2 mcp server**: This server provides functionality for interacting with BMv2 switches, including
  - `bmv2_get_log` to retrieve the log from a BMv2 switch.
  - `bmv2_get_counter_arrays` to retrieve the counter arrays from a BMv2 switch.
- **Frr mcp server**: This server provides functionality for interacting with FRRouting (FRR), including
  - `frr_get_bgp_conf` to retrieve the BGP configuration from a FRR instance.
  - `frr_get_ospf_conf` to retrieve the OSPF configuration from a FRR instance.
- **INT mcp server**: This server provides functionality for interacting with INT (In-band Network Telemetry) data stored in InfluxDB, including
  - `influx_list_buckets` to list all buckets in InfluxDB.
  - `influx_get_measurements` to retrieve the measurements from a specific bucket in InfluxDB.
  - `influx_query_measurement` to query data from InfluxDB.
- **Generic mcp server**: This server provides generic functionalities, including
  - `google_search` to perform a Google search.
- **Task management mcp server**: This server provides functionality for managing tasks and submissions, including
  - `list_avail_problems` to list all available problems for agent to solve.
  - `get_submission_template` to retrieve the submission template for a specific problem.
  - `submit` to submit a solution for a specific problem.

💡 More tools are coming soon...

You can also plug in your own MCP servers following the configuration instruction. Look for more MCP servers at [mcp.so](https://mcp.so/).

### Plug in the servers to your Claude desktop

#### Windows

Since the network environment and kathará run on Linux, and Claude desktop runs on Windows, we need some tricks here.

1. Modify the `xxx_mcp_server.py` files under `src/llm4netlab/service/mcp_server` as follows:
   
```python
mcp = FastMCP(name="kathara_base_mcp_server", host="127.0.0.1", port=8000)
... # your tools can be kept as is
mcp.run(transport="sse")
```

2. Run the server in VSCode terminal, it will automatically forward the port to Windows host, like 8000 -> 8000.

1. Configure Claude's config file `xx/claude_desktop_config.json` as follows:

```json
{
  "mcpServers": {
    "kathara_base": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://127.0.0.1:8000/sse"
      ]
    }
  }
}
```

4. Enjoy!


## Logging and Observability

With mcp-use, LLM4NetLab supports to log and monitor agents with Langfuse, Laminar, and LangSmith, check [mcp-use Observability](https://docs.mcp-use.com/development/observability) and [Langchain Callbacks](https://python.langchain.com/docs/concepts/callbacks/) for details.

### Customized Logger

LLM4NetLab allows users to implement customized logging solutions tailored to their specific needs. This can be achieved by plugging the callback function to `mcp_use.MCPAgent`. For example, 

```python
from langchain.callbacks.base import BaseCallbackHandler

class FileLoggerHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler("mcp_use.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def on_llm_start(self, **kwargs):
        ...

    def on_llm_end(self, **kwargs):
        ...

    def on_tool_start(self,  **kwargs):
        ...

    def on_tool_end(self, **kwargs):
        ...

agent = MCPAgent(
    llm=llm,
    client=client,
    max_steps=max_steps,
    system_prompt_template=system_prompt_template,
    verbose=True,
    callbacks=[FileLoggerHandler()],
)
```

<h1 id="📚cite">📚 Cite</h1>

```bibtex
@inproceedings{wangtowards2025,
author = {Wang, Zhihao and Cornacchia, Alessandro and Galante, Franco and Centofanti, Carlo and Sacco, Alessio and Jiang, Dingde},
title = {Towards a Playground to Democratize Experimentation and Benchmarking of AI Agents for Network Troubleshooting},
year = {2025},
isbn = {9798400720871},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3748496.3748990},
doi = {10.1145/3748496.3748990},
booktitle = {Proceedings of the 1st Workshop on Next-Generation Network Observability},
pages = {1–3},
numpages = {3},
location = {Coimbra, Portugal},
series = {NGNO '25}
}
```

# Acknowledgement

This project is largely motivated by [AIOpsLab](https://github.com/microsoft/AIOpsLab). We sincerely thank the authors for their excellent work.

# Licence

Licensed under the MIT license.