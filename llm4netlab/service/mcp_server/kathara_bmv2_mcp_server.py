from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaBMv2API

# Initialize FastMCP server
mcp = FastMCP("kathara_bmv2_mcp_server")


@mcp.tool()
def bmv2_get_log(lab_name: str, switch_name: str) -> str:
    """Get the logs from the bmv2 switch.

    Args:
        lab_name (str): The name of the lab.
        switch_name (str): The name of the switch.

    Returns:
        str: The logs from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=lab_name)
    return kathara_api.bmv2_get_log(switch_name)


@mcp.tool()
def bmv2_get_counter_arrays(lab_name: str, switch_name: str) -> str:
    """Get the counters from the bmv2 switch.

    Args:
        lab_name (str): The name of the lab.
        switch_name (str): The name of the switch.

    Returns:
        str: The counter names from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=lab_name)
    return kathara_api.bmv2_get_counter_arrays(switch_name)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
