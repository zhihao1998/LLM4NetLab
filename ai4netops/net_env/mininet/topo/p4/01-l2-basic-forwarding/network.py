import os

import zmq
from p4utils.mininetlib.network_API import NetworkAPI

cur_dir = os.path.dirname(os.path.abspath(__file__))

# Set up Mininet environment
net = NetworkAPI()
net.topoFile = os.path.join(cur_dir, "topology.json")

net.setLogLevel("info")
net.setCompiler(p4rt=True)

net.addP4RuntimeSwitch("s1", cli_input=os.path.join(cur_dir, "s1-commands.txt"))
net.setP4Source("s1", os.path.join(cur_dir, "p4src/l2_basic_forwarding.p4"))

net.addHost("h1")
net.addHost("h2")
net.addHost("h3")
net.addHost("h4")

net.addLink("s1", "h1")
net.addLink("s1", "h2")
net.addLink("s1", "h3")
net.addLink("s1", "h4")

net.l2()
net.enablePcapDumpAll(os.path.join(cur_dir, "pcap"))
net.enableLogAll(os.path.join(cur_dir, "log"))
net.disableCli()

net.startNetwork()

# 启动 ZeroMQ REP 服务
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

try:
    while True:
        message = socket.recv_string()
        print(f"📥 收到命令: {message}")

        # 解析命令
        parts = message.strip().split()
        if not parts:
            socket.send_string("❌ 无效命令")
            continue

        cmd = parts[0]

        if cmd == "status":
            socket.send_string("ok")
        elif cmd == "ping" and len(parts) == 3:
            h1 = net.net.get(parts[1])
            h2 = parts[2]
            result = h1.cmd(f"ping -c 3 {h2}")
            socket.send_string(result)

        elif cmd == "exec" and len(parts) >= 3:
            host = net.net.get(parts[1])
            shell_cmd = " ".join(parts[2:])
            result = host.cmd(shell_cmd)
            socket.send_string(result)

        elif cmd == "exit":
            socket.send_string("✅ 退出 Mininet 服务")
            break

        elif cmd == "linkdown" and len(parts) == 3:
            h1 = parts[1]
            h2 = parts[2]
            net.net.configLinkStatus(h1, h2, "down")
            socket.send_string(f"🔴 {h1} 和 {h2} 之间的链路已关闭")

        elif cmd == "linkup" and len(parts) == 3:
            h1 = parts[1]
            h2 = parts[2]
            net.net.configLinkStatus(h1, h2, "up")
            socket.send_string(f"🟢 {h1} 和 {h2} 之间的链路已恢复")

        else:
            socket.send_string("❌ 未知命令或参数不足")

except KeyboardInterrupt:
    print("🔴 手动中断")

finally:
    net.stopNetwork()
    print("🛑 Mininet 已关闭")
