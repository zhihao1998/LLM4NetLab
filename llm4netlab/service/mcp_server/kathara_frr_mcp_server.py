from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaFRRAPI

# Initialize FastMCP server
mcp = FastMCP("kathara_bmv2_mcp_server")


@mcp.tool()
def frr_get_bgp_conf(lab_name: str, router_name: str) -> str:
    """Get the BGP configuration from the FRR router.

    Args:
        lab_name (str): The name of the lab.
        router_name (str): The name of the router.

    Returns:
        str: The BGP configuration from the FRR router.
    """
    kathara_api = KatharaFRRAPI(lab_name=lab_name)
    return kathara_api.frr_get_bgp_conf(router_name)


@mcp.tool()
def frr_get_ospf_conf(lab_name: str, router_name: str) -> str:
    """Get the OSPF configuration from the FRR router.

    Args:
        lab_name (str): The name of the lab.
        router_name (str): The name of the router.

    Returns:
        str: The OSPF configuration from the FRR router.
    """
    kathara_api = KatharaFRRAPI(lab_name=lab_name)
    return kathara_api.frr_get_ospf_conf(router_name)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
