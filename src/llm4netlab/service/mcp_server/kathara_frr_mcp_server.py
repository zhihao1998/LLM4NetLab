import os

from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaFRRAPI
from llm4netlab.utils.errors import safe_tool

# Initialize FastMCP server
mcp = FastMCP("kathara_bmv2_mcp_server")
LAB_NAME = os.getenv("LAB_NAME")


@safe_tool
@mcp.tool()
def frr_get_bgp_conf(router_name: str) -> str:
    """Get the BGP configuration from the FRR router.

    Args:
        router_name (str): The name of the router.

    Returns:
        str: The BGP configuration from the FRR router.
    """
    kathara_api = KatharaFRRAPI(lab_name=LAB_NAME)
    return kathara_api.frr_get_bgp_conf(router_name)


@safe_tool
@mcp.tool()
def frr_show_running_config(router_name: str) -> str:
    """Get the running configuration from the FRR router.

    Args:
        router_name (str): The name of the router.
    Returns:
        str: The running configuration from the FRR router.
    """
    kathara_api = KatharaFRRAPI(lab_name=LAB_NAME)
    return kathara_api.frr_show_running_config(router_name)


@safe_tool
@mcp.tool()
def frr_show_ip_route(router_name: str) -> str:
    """Get the IP routing table from the FRR router.

    Args:
        router_name (str): The name of the router.
    Returns:
        str: The IP routing table from the FRR router.
    """
    kathara_api = KatharaFRRAPI(lab_name=LAB_NAME)
    return kathara_api.frr_show_route(router_name)


@safe_tool
@mcp.tool()
def frr_get_ospf_conf(router_name: str) -> str:
    """Get the OSPF configuration from the FRR router.

    Args:
        router_name (str): The name of the router.

    Returns:
        str: The OSPF configuration from the FRR router.
    """
    kathara_api = KatharaFRRAPI(lab_name=LAB_NAME)
    return kathara_api.frr_get_ospf_conf(router_name)


@safe_tool
@mcp.tool()
def frr_exec(router_name: str, command: str) -> str:
    """Execute a vtysh command on a FRR router."""
    kathara_api = KatharaFRRAPI(lab_name=LAB_NAME)
    return kathara_api.frr_exec(router_name, command)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
