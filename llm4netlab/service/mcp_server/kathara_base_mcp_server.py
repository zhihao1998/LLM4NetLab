from mcp.server.fastmcp import FastMCP

from llm4netlab.service.kathara import KatharaBaseAPI, KatharaNFTableAPI

# Initialize FastMCP server
mcp = FastMCP("kathara_base_mcp_server")


@mcp.tool()
async def get_reachability(lab_name: str) -> str:
    """Get the reachability of the net_env. From each host, it checks if it can ping all other hosts.

    Args:
        lab_name (str): The name of the lab.

    Returns:
        str: The ping results from each host to all other hosts in the lab.
    """
    kathara_api = KatharaBaseAPI(lab_name=lab_name)
    result = await kathara_api.get_reachability()
    return result


@mcp.tool()
def systemctl_ops(lab_name: str, host_name: str, service_name: str, operation: str) -> str:
    """Perform systemctl operations (start, stop, restart, status) on a host.

    Args:
        lab_name (str): The name of the lab.
        host_name (str): The name of the host.
        service_name (str): The name of the service.
        operation (str): The operation to perform (start, stop, restart, status).

    Returns:
        str: The output of the systemctl command.
    """
    kathara_api = KatharaBaseAPI(lab_name=lab_name)
    result = kathara_api.systemctl_ops(host_name=host_name, service_name=service_name, operation=operation)
    return result


@mcp.tool()
def get_host_net_config(lab_name: str, host_name: str) -> dict:
    """Get the network configuration of a host, including ifconfig, ip addr, and ip route.

    Args:
        lab_name (str): The name of the lab.
        host_name (str): The name of the host.

    Returns:
        dict: The network configuration of the host.
    """
    kathara_api = KatharaBaseAPI(lab_name=lab_name)
    config = kathara_api.get_host_net_config(host_name=host_name)
    return config


@mcp.tool()
def iperf_test(
    lab_name: str,
    client_host_name: str,
    server_host_name: str,
    duration: int = 10,
    client_args: str = "",
    server_args: str = "",
) -> str:
    """Run an iperf test between two hosts in the lab.

    Args:
        lab_name (str): The name of the lab.
        client_host_name (str): Name of the client host.
        server_host_name (str): Name of the server host.
        duration (int, optional): Duration of the test in seconds. Defaults to 10.
        client_args (str, optional): Additional arguments for the client. Defaults to "".
        server_args (str, optional): Additional arguments for the server. Defaults to "".

    Returns:
        str: The output of the iperf test.
    """
    kathara_api = KatharaBaseAPI(lab_name=lab_name)
    result = kathara_api.iperf_test(
        client_host_name=client_host_name,
        server_host_name=server_host_name,
        duration=duration,
        client_args=client_args,
        server_args=server_args,
    )
    return result


@mcp.tool()
def nft_list_ruleset(lab_name: str) -> dict:
    """Get the nftables ruleset for the lab.

    Args:
        lab_name (str): The name of the lab.

    Returns:
        dict: The nftables ruleset.
    """
    kathara_api = KatharaNFTableAPI(lab_name=lab_name)
    ruleset = kathara_api.nft_list_ruleset()
    return ruleset


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
