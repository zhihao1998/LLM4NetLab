import os

from mcp.server.fastmcp import FastMCP

from llm4netlab.net_env.kathara.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.service.kathara import KatharaBaseAPI
from llm4netlab.service.kathara.frr_api import KatharaFRRAPI

# Initialize FastMCP server
mcp = FastMCP(name="kathara_base_mcp_server", host="127.0.0.1", port=8000, log_level="DEBUG")
LAB_NAME = os.getenv("LAB_NAME", "simple_bgp")


@mcp.tool()
def get_net_env_info() -> dict:
    """Get basic information about the net_env, including hosts, routers, and links.

    Returns:
        dict: A dictionary containing the information of the network.
    """
    lab = SimpleBGP()
    info = lab.get_info()
    return info


@mcp.tool()
async def get_reachability() -> str:
    """Get the reachability of the net_env. From each host, it checks if it can ping all other hosts.

    Returns:
        str: The ping results from each host to all other hosts in the lab.
    """
    kathara_api = KatharaBaseAPI(lab_name=LAB_NAME)
    result = await kathara_api.get_reachability()
    return result


@mcp.tool()
def systemctl_ops(host_name: str, service_name: str, operation: str) -> str:
    """Perform systemctl operations (start, stop, restart, status) on a host.

    Args:
        host_name (str): The name of the host.
        service_name (str): The name of the service.
        operation (str): The operation to perform (start, stop, restart, status).

    Returns:
        str: The output of the systemctl command.
    """
    kathara_api = KatharaBaseAPI(lab_name=LAB_NAME)
    result = kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation=operation)
    return result


@mcp.tool()
def get_host_net_config(host_name: str) -> dict:
    """Get the network configuration of a host, including ifconfig, ip addr, and ip route.

    Args:
        host_name (str): The name of the host.

    Returns:
        dict: The network configuration of the host.
    """
    kathara_api = KatharaBaseAPI(lab_name=LAB_NAME)
    config = kathara_api.get_host_net_config(host_name=host_name)
    return config


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
def iperf_test(
    client_host_name: str,
    server_host_name: str,
    duration: int = 10,
    client_args: str = "",
    server_args: str = "",
) -> str:
    """Run an iperf test between two hosts in the lab.

    Args:
        client_host_name (str): Name of the client host.
        server_host_name (str): Name of the server host.
        duration (int, optional): Duration of the test in seconds. Defaults to 10.
        client_args (str, optional): Additional arguments for the client. Defaults to "".
        server_args (str, optional): Additional arguments for the server. Defaults to "".

    Returns:
        str: The output of the iperf test.
    """
    kathara_api = KatharaBaseAPI(lab_name=LAB_NAME)
    result = kathara_api.iperf_test(
        client_host_name=client_host_name,
        server_host_name=server_host_name,
        duration=duration,
        client_args=client_args,
        server_args=server_args,
    )
    return result


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
    # print(get_net_env_info())
