import os
import signal
import subprocess
import time

import zmq


class MininetEnv:
    def __init__(
        self,
        server_script="/home/p4/AI4NetOps/ai4netops/net_env/mininet/topo/p4/01-l2-basic-forwarding/network.py",
        port=5555,
    ):
        self.server_script = server_script
        self.port = port
        self.process = None
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

    def start(self):
        print("🚀 启动 Mininet 服务脚本...")
        self.process = subprocess.Popen(
            ["sudo", "python3", self.server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,  # 启动为新进程组
        )

        # 等待 ZMQ 服务上线
        print("⏳ 等待 ZeroMQ 接口响应...")
        self._wait_for_zmq()

        # 连接到 ZeroMQ
        self.socket.connect(f"tcp://localhost:{self.port}")
        print("✅ Mininet 服务已连接")

    def _wait_for_zmq(self, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                test_socket = self.context.socket(zmq.REQ)
                test_socket.connect(f"tcp://localhost:{self.port}")
                test_socket.setsockopt(zmq.LINGER, 0)
                test_socket.send_string("status")
                poller = zmq.Poller()
                poller.register(test_socket, zmq.POLLIN)
                if poller.poll(1000):
                    response = test_socket.recv_string()
                    if response.strip() == "ok":
                        print("✅ ZeroMQ 服务已准备")
                        test_socket.close()
                        return
                test_socket.close()
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError("⚠️ ZeroMQ 服务器连接超时")

    def send(self, cmd):
        print(f"📤 发送命令: {cmd}")
        self.socket.send_string(cmd)
        response = self.socket.recv_string()
        print(f"📥 响应:\n{response}\n")
        return response

    def stop(self):
        print("🛑 正在停止 Mininet 环境...")
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                stdout, stderr = self.process.communicate(timeout=5)
                print("📝 Mininet 输出:\n", stdout.decode())
                if stderr:
                    print("⚠️ 错误信息:\n", stderr.decode())
            except Exception as e:
                print("❌ 关闭时异常：", str(e))
        self.socket.close()
        self.context.term()


# -------------------------------------------
# ✅ 调试入口
# -------------------------------------------

if __name__ == "__main__":
    env = MininetEnv()

    try:
        env.start()
        env.send("exec h1 ifconfig")
        env.send("exec h2 hostname")

        env.send("ping h1 10.0.0.2")

        env.send("linkdown h1 s1")
        env.send("ping h1 10.0.0.2")
        env.send("linkup h1 s1")
        time.sleep(1)
        env.send("ping h1 10.0.0.2")

        env.send("exit")
    except Exception as e:
        print("❌ 运行时错误：", str(e))
    finally:
        env.stop()
