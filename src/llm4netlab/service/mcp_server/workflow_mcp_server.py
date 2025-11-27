import os
from pathlib import Path
import yaml

from dotenv import load_dotenv
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from llm4netlab.utils.errors import safe_tool


# ============================
# Load ENV
# ============================
load_dotenv()


# ============================
# Init MCP Server
# ============================
mcp = FastMCP("workflow_mcp_server")


# ============================
# Workflow Directory
# ============================
BASE_DIR = os.getenv("BASE_DIR")

WORKFLOW_DIR = Path(BASE_DIR) / "src" / "llm4netlab" / "orchestrator" / "workflows"

WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)



# ============================
# MCP Tool Definition
# ============================
@safe_tool
@mcp.tool()
def get_workflow(fault_group: str) -> str:
    """
    Load workflow steps for a suspected fault category.

    Args:
        fault_group (str): Must be strictly one of the following 18 categories:
            acl_block / arp_attack / link_failure / host_ip_config / host_dns_config /
            link_performance / p4_compile_error / p4_table_error / bgp_issue /
            ospf_issue / sdn_southbound / flow_rule_conflict / dhcp_issue /
            dns_service / dns_lookup_latency / load_balancer_overload /
            link_fragmentation_disabled / mpls_label_limit

    Returns:
        str:  The complete system prompt (directly usable as a SystemMessage injection)
    """

    limited_fault_groups = [
        "acl_block",
        "arp_attack",
        "link_failure",
        "host_ip_config",
        "host_dns_config",
        "link_performance",
        "p4_compile_error",
        "p4_table_error",
        "bgp_issue",
        "ospf_issue",
        "sdn_southbound",
        "flow_rule_conflict",
        "dhcp_issue",
        "dns_service",
        "dns_lookup_latency",
        "load_balancer_overload",
        "link_fragmentation_disabled",
        "mpls_label_limit",
    ]

    if fault_group not in limited_fault_groups:
        raise ValueError(f"Invalid fault group: {fault_group}, must be one of {limited_fault_groups}")

    file_name = f"{fault_group}.txt"

    workflow_baseFile = WORKFLOW_DIR / "base.txt"
    workflow_file = WORKFLOW_DIR / file_name

    if not workflow_file.exists():
        raise FileNotFoundError(f"Workflow not found: {workflow_file}")

    return workflow_baseFile.read_text(encoding="utf-8") + "\n" + workflow_file.read_text(encoding="utf-8")


# ============================
# Start Server
# ============================
if __name__ == "__main__":
    # result = get_workflow("temp")  # test load
    # print(result)
    mcp.run(transport="stdio")