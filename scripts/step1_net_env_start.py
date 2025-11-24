import argparse
import logging

from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.utils.session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_kv(s):
    if "=" not in s:
        raise argparse.ArgumentTypeError("Parameters must be in key=value format")
    key, value = s.split("=", 1)
    try:
        value = int(value)
    except ValueError:
        pass
    return key, value


def start_net_env(scenario_name: str, **kwargs):
    """
    Every run starts a new session.
    """
    net_env = get_net_env_instance(scenario_name, **kwargs)
    net_env.deploy()

    # save session data for follow-up steps
    session = Session()
    session.init_session()
    session.update_session("scenario_name", scenario_name)
    session.update_session("scenario_params", kwargs)
    logger.info(f"Started network environment: {scenario_name} with session ID: {session.session_id}")
    return net_env


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Network Environment")

    parser.add_argument(
        "--scenario",
        type=str,
        default="simple_bgp",
        help="Name of the network environment to start (default: simple_bgp)",
    )

    parser.add_argument(
        "--scenario_params",
        nargs="*",
        type=parse_kv,
        default=[("router_num", 2)],
        help="Dynamic key=value pairs (e.g. --scenario_params router_num=2 as_number=65001)",
    )

    args = parser.parse_args()

    params = dict(args.scenario_params)
    start_net_env(args.scenario, **params)
