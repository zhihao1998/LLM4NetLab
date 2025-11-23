import argparse
import logging

from llm4netlab.net_env.net_env_pool import get_net_env_instance
from llm4netlab.utils.session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def end_net_env():
    """
    Destroy the network environment associated with the current session.
    """
    session = Session()
    session.load_running_session()

    net_env = get_net_env_instance(session.net_env_name)
    net_env.undeploy()
    logger.info(f"Destroyed network environment: {session.net_env_name} with session ID: {session.session_id}")
    session.clear_session()
    return net_env


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End Network Environment")
    args = parser.parse_args()

    end_net_env()
