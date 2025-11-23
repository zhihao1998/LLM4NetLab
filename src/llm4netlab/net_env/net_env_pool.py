from typing import Dict

from llm4netlab.net_env.base import NetworkEnvBase
from llm4netlab.net_env.data_center_routing.dc_clos_bgp.lab import DCClosBGP
from llm4netlab.net_env.data_center_routing.dc_clos_service.lab import DCClosService
from llm4netlab.net_env.interdomain_routing.simple_bgp.lab import SimpleBGP
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_dhcp import OSPFEnterpriseDHCP
from llm4netlab.net_env.intradomain_routing.ospf_enterprise.lab_static import OSPFEnterpriseStatic
from llm4netlab.net_env.p4.p4_bloom_filter.lab import P4BloomFilter
from llm4netlab.net_env.p4.p4_counter.lab import P4Counter
from llm4netlab.net_env.p4.p4_int.lab import P4INT
from llm4netlab.net_env.sdn.lab import SDNOpenFlow

_NET_ENVS: Dict[str, NetworkEnvBase] = {
    "dc_clos_bgp": DCClosBGP,
    "dc_clos_service": DCClosService,
    "simple_bgp": SimpleBGP,
    "ospf_enterprise_dhcp": OSPFEnterpriseDHCP,
    "ospf_enterprise_static": OSPFEnterpriseStatic,
    "p4_bloom_filter": P4BloomFilter,
    "p4_counter": P4Counter,
    "p4_int": P4INT,
    "sdn_openflow": SDNOpenFlow,
}


def get_net_env_instance(net_env_name: str, **kwargs) -> NetworkEnvBase:
    """Get an instance of the specified network environment.

    Args:
        net_env_name: The name of the network environment.

    Returns:
        An instance of the specified network environment.

    Raises:
        ValueError: If the specified network environment is not found.
    """
    if net_env_name not in _NET_ENVS:
        raise ValueError(f"Network environment '{net_env_name}' not found in the pool.")
    return _NET_ENVS[net_env_name](**kwargs)


if __name__ == "__main__":
    for env_name, env_class in _NET_ENVS.items():
        env_instance = env_class()
        print(f"Network Environment: {env_name}")

    lab = get_net_env_instance("dc_clos_bgp", super_spine_count=3)
    print(lab.routers)
