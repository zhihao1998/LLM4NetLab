import os

from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaFRRAPI

# Initialize FastMCP server
mcp = FastMCP("kathara_bmv2_mcp_server")
LAB_NAME = os.getenv("LAB_NAME")


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


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
