from ai4netops.config import MININET_SERVER_ADDR
from ai4netops.service.mininet_api import MininetAPI


class WorkloadMininet:
    """Workload Generator for Mininet Network."""

    def __init__(self):
        super().__init__()
        self.mininet_api = MininetAPI(mininet_server_addr=MININET_SERVER_ADDR)
        self.mininet_api.connect()
        assert self.mininet_api.test_mn_connect()

    def ping_pair(self, h1: str = "h1", h2: str = "10.0.0.2"):
        """Ping between two hosts in the Mininet environment."""
        response = self.mininet_api.ping_pair(h1, h2)
        return response


if __name__ == "__main__":
    workload = WorkloadMininet()
    print(workload.ping_pair("h1", "10.0.0.3"))
