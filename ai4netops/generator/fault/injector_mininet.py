import time

from ai4netops.config import MININET_SERVER_ADDR
from ai4netops.generator.fault.injector_base import BaseFaultInjector
from ai4netops.service.mininet_api import MininetAPI


class FaultInjectorMininet(BaseFaultInjector):
    """Fault injector for Mininet Network."""

    def __init__(self):
        super().__init__()
        self.mininet_api = MininetAPI(mininet_server_addr=MININET_SERVER_ADDR)
        self.mininet_api.connect()
        assert self.mininet_api.test_mn_connect()

    # TODO: specify the link dynamically
    def inject_link_down(self, node1: str = "h1", node2: str = "s1"):
        """Inject a link down fault between two nodes."""
        self.mininet_api.link_down(node1, node2)

    def recover_link_down(self, node1: str = "h1", node2: str = "s1"):
        """Recover a link down fault between two nodes."""
        self.mininet_api.link_up(node1, node2)


if __name__ == "__main__":
    injector = FaultInjectorMininet()

    injector.inject_link_down("h1", "s1")
    print("Link down injected")
    time.sleep(5)
    injector.recover_link_down("h1", "s1")
    print("Link down recovered")
