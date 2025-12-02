import os

from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaBMv2API
from llm4netlab.utils.errors import safe_tool

# Initialize FastMCP server
mcp = FastMCP("kathara_bmv2_mcp_server")
LAB_NAME = os.getenv("LAB_NAME")


@safe_tool
@mcp.tool()
def bmv2_get_log(switch_name: str, rows: int) -> str:
    """Get the logs from the bmv2 switch. Be careful when using this tool as the log size can be very large.
    Args:
        switch_name (str): The name of the switch.
        rows (int): Number of log lines to retrieve.

    Returns:
        str: The logs from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_get_log(switch_name, rows)


@safe_tool
@mcp.tool()
def bmv2_get_counter_arrays(switch_name: str) -> str:
    """Get the counters from the bmv2 switch.

    Args:
        switch_name (str): The name of the switch.

    Returns:
        str: The counter names from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_get_counter_arrays(switch_name)


@safe_tool
@mcp.tool()
def bmv2_read_p4_program(switch_name: str) -> str:
    """Read the P4 program from the bmv2 switch.

    Args:
        switch_name (str): The name of the switch.
    Returns:
        str: The P4 program from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.read_p4_program(switch_name)


@safe_tool
@mcp.tool()
def bmv2_counter_read(switch_name: str, counter_name: str, index: int = 0) -> str:
    """Read a counter from the bmv2 switch.

    Args:
        switch_name (str): The name of the switch.
        counter_name (str): The name of the counter.
        index (int, optional): The index of the counter. Defaults to 0.

    Returns:
        str: The counter value from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_counter_read(switch_name, counter_name, index)


@safe_tool
@mcp.tool()
def bmv2_show_tables(switch_name: str) -> str:
    """Show all tables of a bmv2 switch.

    Args:
        switch_name (str): The name of the switch.

    Returns:
        str: The table names from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_show_tables(switch_name)


@safe_tool
@mcp.tool()
def bmv2_table_dump(switch_name: str, table_name: str) -> str:
    """Dump a table from the bmv2 switch.

    Args:
        switch_name (str): The name of the switch.
        table_name (str): The name of the table.

    Returns:
        str: The table entries from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_table_dump(switch_name, table_name)


@safe_tool
@mcp.tool()
def bmv2_get_register_arrays(switch_name: str) -> str:
    """Get the register arrays from the bmv2 switch.
    Args:
        switch_name (str): The name of the switch.
    Returns:
        str: The register array names from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_get_register_arrays(switch_name)


@safe_tool
@mcp.tool()
def bmv2_register_read(
    switch_name: str,
    register_name: str,
    index: int = 0,
) -> str:
    """Read a register from the bmv2 switch.
    Args:
        switch_name (str): The name of the switch.
        register_name (str): The name of the register.
        index (int, optional): The index of the register. Defaults to 0.
    Returns:
        str: The register value from the bmv2 switch.
    """
    kathara_api = KatharaBMv2API(lab_name=LAB_NAME)
    return kathara_api.bmv2_register_read(switch_name, register_name, index)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
