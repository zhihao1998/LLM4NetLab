from typing import Dict

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.data_center_routing.dc_clos_bgp.lab_services import DCClosService
from llm4netlab.net_env.data_center_routing.dc_clos_bgp.lab_workers import DCClosBGP
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterpriseDHCP
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.net_env.intradomain_routing.rip_vpn.lab import RIPSmallInternetVPN
from llm4netlab.net_env.p4.p4_bloom_filter.lab import P4BloomFilter
from llm4netlab.net_env.p4.p4_counter.lab import P4Counter
from llm4netlab.net_env.p4.p4_int.lab import P4INT
from llm4netlab.net_env.p4.p4_mpls.lab import P4_MPLS
from llm4netlab.net_env.sdn.clos_topo import SDNClos
from llm4netlab.net_env.sdn.star_topo import SDNStar

_NET_ENVS: Dict[str, NetworkEnvBase] = {
    DCClosBGP.LAB_NAME: DCClosBGP,
    DCClosService.LAB_NAME: DCClosService,
    OSPFEnterpriseDHCP.LAB_NAME: OSPFEnterpriseDHCP,
    OSPFEnterpriseStatic.LAB_NAME: OSPFEnterpriseStatic,
    RIPSmallInternetVPN.LAB_NAME: RIPSmallInternetVPN,
    SDNStar.LAB_NAME: SDNStar,
    SDNClos.LAB_NAME: SDNClos,
    P4BloomFilter.LAB_NAME: P4BloomFilter,
    P4Counter.LAB_NAME: P4Counter,
    P4INT.LAB_NAME: P4INT,
    P4_MPLS.LAB_NAME: P4_MPLS,
}


def get_net_env_instance(scenario_name: str, **kwargs) -> NetworkEnvBase:
    """Get an instance of the specified network environment.

    Args:
        scenario_name: The name of the network environment.

    Returns:
        An instance of the specified network environment.

    Raises:
        ValueError: If the specified network environment is not found.
    """
    if scenario_name not in _NET_ENVS:
        raise ValueError(f"Network environment '{scenario_name}' not found in the pool.")
    return _NET_ENVS[scenario_name](**kwargs)


def list_all_net_envs() -> dict[str, NetworkEnvBase]:
    """List all available network environment names."""
    return _NET_ENVS


if __name__ == "__main__":
    import json

    res = {}
    for env_name, env_class in _NET_ENVS.items():
        env_instance = env_class()
        res[env_name] = {
            "resizeable": True,
        }
    print(json.dumps(res, indent=4))

    lab = get_net_env_instance(
        "dc_clos_bgp",
        topo_size="l",
    )
    print(lab.routers)
