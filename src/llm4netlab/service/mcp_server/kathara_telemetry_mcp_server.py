import os

from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaTelemetryAPI
from llm4netlab.utils.errors import safe_tool

# Initialize FastMCP server
mcp = FastMCP("kathara_telemetry_mcp_server")
LAB_NAME = os.getenv("LAB_NAME")


@safe_tool
@mcp.tool()
def influx_list_buckets() -> list[str]:
    """List all InfluxDB buckets.

    Returns:
        list[str]: A list of InfluxDB bucket names, default in json format.
    """
    kathara_api = KatharaTelemetryAPI(lab_name=LAB_NAME)
    return kathara_api.influx_list_buckets()


@safe_tool
@mcp.tool()
def influx_get_measurements() -> list[str]:
    """List all InfluxDB measurements.

    Returns:
        list[str]: A list of InfluxDB measurement names.
    """
    kathara_api = KatharaTelemetryAPI(lab_name=LAB_NAME)
    return kathara_api.influx_get_measurements()


@safe_tool
@mcp.tool()
def influx_count_measurements(measurement: str) -> list[str]:
    """Count the number of records in an InfluxDB measurement.

    Args:
        measurement (str): The name of the measurement.

    Returns:
        list[str]: The count of records in the measurement, default in json format.
    """
    kathara_api = KatharaTelemetryAPI(lab_name=LAB_NAME)
    return kathara_api.influx_count_measurements(measurement)


@safe_tool
@mcp.tool()
def influx_query_measurement(measurement: str, limit: int = 10, offset: int = 0) -> list[str]:
    """Query an InfluxDB measurement.
    Large Dataset Warning: InfluxDB might contain massive time-series data.
    Always use influx_count_measurements() first to check size, then LIMIT/OFFSET for large results (>1000 rows).

    Args:
        measurement (str): The name of the measurement.
        limit (int, optional): The maximum number of records to return. Defaults to 10.
        offset (int, optional): The number of records to skip. Defaults to 0.

    Returns:
        list[str]: The queried records from the measurement, default in json format.
    """
    kathara_api = KatharaTelemetryAPI(lab_name=LAB_NAME)
    return kathara_api.influx_query_measurement(measurement, limit=limit, offset=offset)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
