import zmq

from ai4netops.config import MININET_SERVER_ADDR


class MininetAPI:
    """Mininet API for controlling the Mininet environment."""

    def __init__(self, mininet_server_addr=MININET_SERVER_ADDR):
        self.mininet_server_addr = mininet_server_addr
        self.context = None
        self.socket = None

    def connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.mininet_server_addr)

    def close(self):
        self.socket.close()
        self.context.term()

    def _send_cmd(self, cmd, timeout_ms=3000):
        """Send a command to the Mininet server and wait for a response.
        Args:
            cmd (str): The command to send.
            timeout_ms (int): Timeout in milliseconds.
        """
        self.socket.send_string(cmd)

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        events = dict(poller.poll(timeout_ms))

        if self.socket in events:
            return self.socket.recv_string()
        else:
            raise TimeoutError(f"❌ Timeout: No response from Mininet server for command '{cmd}'")

    def test_mn_connect(self):
        """Test the connection to the Mininet environment."""
        cmd = "status"
        response = self._send_cmd(cmd)
        if response.strip() == "ok":
            return True
        else:
            return False

    def ping_pair(self, h1: str, h2: str):
        """Ping between two hosts in the Mininet environment.

        Args:
            h1 (str): The name of the first host.
            h2 (str): The name/IP of the second host.
        """
        cmd = f"ping {h1} {h2}"
        response = self._send_cmd(cmd)
        return response

    def host_exec(self, host: str, command: str):
        """Execute a command on a specific host in the Mininet environment.

        Args:
            host (str): The name of the host.
            command (str): The command to execute.
        """
        cmd = f"exec {host} {command}"
        response = self._send_cmd(cmd)
        return response

    def host_ifconfig(self, host: str):
        """Get the ifconfig output of a specific host in the Mininet environment.

        Args:
            host (str): The name of the host.
        """
        cmd = f"exec {host} ifconfig"
        response = self._send_cmd(cmd)
        return response

    def link_down(self, h1: str, h2: str):
        """Bring down the link between two nodes(host/switch) in the Mininet environment.

        Args:
            h1 (str): The name of the first node.
            h2 (str): The name of the second node.
        """
        cmd = f"linkdown {h1} {h2}"
        response = self._send_cmd(cmd)
        if response.strip() == "ok":
            return response
        else:
            raise Exception(f"❌ Failed to bring down the link between {h1} and {h2}: {response}")

    def link_up(self, h1: str, h2: str):
        """Bring up the link between two nodes(host/switch) in the Mininet environment.

        Args:
            h1 (str): The name of the first node.
            h2 (str): The name of the second node.
        """
        cmd = f"linkup {h1} {h2}"
        response = self._send_cmd(cmd)
        if response.strip() == "ok":
            return response
        else:
            raise Exception(f"❌ Failed to bring up the link between {h1} and {h2}: {response}")

    def dump_conn(self):
        """Dump the connection information of all hosts in the Mininet environment."""
        cmd = "dumpconn"
        response = self._send_cmd(cmd)
        return response


if __name__ == "__main__":
    mn_api = MininetAPI()
    mn_api.connect()
    assert mn_api.test_mn_connect()

    # Example usage
    print(mn_api.ping_pair("h1", "10.0.0.2"))
    print(mn_api.host_exec("h1", "ls"))
    print(mn_api.host_ifconfig("h1"))
    print(mn_api.link_down("h1", "s1"))
    print(mn_api.ping_pair("h1", "10.0.0.2"))
    print(mn_api.dump_conn())
    print(mn_api.host_ifconfig("h1"))
    print(mn_api.link_up("h1", "s1"))
    print(mn_api.ping_pair("h1", "10.0.0.2"))
    print(mn_api.dump_conn())
    mn_api.close()
