import os
import signal
import subprocess
import time

from ai4netops.service.mininet_api import MininetAPI


class MininetEnv:
    """
    Note: need to keep this along each experiment to avoid
    """

    def __init__(
        self,
        server_script="/home/p4/AI4NetOps/ai4netops/net_env/mininet/topo/p4/01-l2-basic-forwarding/network.py",
        port=5555,
    ):
        self.server_script = server_script
        self.port = port
        self.process = None
        self.mininet_api = MininetAPI(mininet_server_addr=f"tcp://localhost:{self.port}")

    def start(self):
        print("🚀 Starting Mininet Environment...")
        self.process = subprocess.Popen(
            ["sudo", "python3", self.server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )

        print("⏳ Waiting for Mininet to start...")
        self._wait_for_zmq(timeout=10)

    def _wait_for_zmq(self, timeout=10):
        start = time.time()
        self.mininet_api.connect()
        while time.time() - start < timeout:
            try:
                # Test if the Mininet server is ready
                if self.mininet_api.test_mn_connect():
                    print("✅ Mininet server is ready")
                    return
            except Exception:
                pass
            finally:
                # Close the socket to avoid resource leaks
                self.mininet_api.close()
            time.sleep(1)
        raise TimeoutError("⚠️ ZeroMQ server did not start in time")

    def stop(self):
        print("🛑 Stopping Mininet Environment")
        # try normal exit
        if self.mininet_api:
            try:
                self.mininet_api.connect()
                # self.mininet_api._send_cmd("exit")
            except Exception as e:
                print("❌ Exception while stopping Mininet with exit:", str(e), "\nTrying to kill process...")

        # try kill process
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                stdout, stderr = self.process.communicate(timeout=5)
                print("📝 Mininet Output:\n", stdout.decode())
                if stderr:
                    print("⚠️ Debug Information:\n", stderr.decode())
            except Exception as e:
                print("❌ Exception while stopping Mininet:", str(e))


# -------------------------------------------
# ✅ Simple Test
# -------------------------------------------

if __name__ == "__main__":
    env = MininetEnv()

    try:
        env.start()
    except Exception as e:
        print("❌ Exception:", str(e))
    finally:
        env.stop()
