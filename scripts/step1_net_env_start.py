import argparse
import logging

from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.utils.session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_kv(s):
    key, value = s.split("=", 1)
    return key, value


def start_net_env(net_env_name: str, **kwargs):
    """
    Every run starts a new session.
    """
    net_env = get_net_env_instance(net_env_name, **kwargs)
    net_env.deploy()

    # save session data for follow-up steps
    session = Session()
    session.init_session()
    session.update_session("net_env_name", net_env_name)
    session.update_session("net_env_params", kwargs)
    logger.info(f"Started network environment: {net_env_name} with session ID: {session.session_id}")
    return net_env


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Network Environment")
    parser.add_argument(
        "net_env_name",
        type=str,
        nargs="?",
        default="simple_bgp",
        help="Name of the network environment to start (default: simple_bgp)",
    )
    parser.add_argument("net_env_params", nargs="*", type=parse_kv, default=[], help="Dynamic key=value pairs")
    args = parser.parse_args()

    # Start the network environment
    params = dict(args.net_env_params)
    start_net_env(args.net_env_name, **params)
