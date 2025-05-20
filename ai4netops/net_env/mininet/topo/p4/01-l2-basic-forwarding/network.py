import os
import sys

import zmq
from p4utils.mininetlib.network_API import NetworkAPI

# todo: need a better way to set the path
sys.path.append("/home/p4/AI4NetOps")
from ai4netops.utils.mininet_utils import dumpNetConnections

cur_dir = os.path.dirname(os.path.abspath(__file__))

# Set up Mininet environment
mn_api = NetworkAPI()
mn_api.topoFile = os.path.join(cur_dir, "topology.json")
mn_api.modules["sw_cli"]["kwargs"] = {"log_dir": os.path.join(cur_dir, "log")}

mn_api.setLogLevel("info")
mn_api.setCompiler(p4rt=True)

mn_api.addP4RuntimeSwitch("s1", cli_input=os.path.join(cur_dir, "s1-commands.txt"))
mn_api.setP4Source("s1", os.path.join(cur_dir, "p4src/l2_basic_forwarding.p4"))

mn_api.addHost("h1")
mn_api.addHost("h2")
mn_api.addHost("h3")
mn_api.addHost("h4")

mn_api.addLink("s1", "h1")
mn_api.addLink("s1", "h2")
mn_api.addLink("s1", "h3")
mn_api.addLink("s1", "h4")

mn_api.l2()
mn_api.enablePcapDumpAll(os.path.join(cur_dir, "pcap"))
mn_api.enableLogAll(os.path.join(cur_dir, "log"))
mn_api.disableCli()

mn_api.startNetwork()

# 启动 ZeroMQ REP 服务
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

try:
    while True:
        message = socket.recv_string()
        print(f"📥 Received command: {message}")

        parts = message.strip().split()
        if not parts:
            socket.send_string("❌ Invalid command")
            continue

        cmd = parts[0]

        if cmd == "status":
            if mn_api.net is not None:
                socket.send_string("ok")

        elif cmd == "ping" and len(parts) == 3:
            h1 = mn_api.net.get(parts[1])
            h2 = parts[2]
            result = h1.cmd(f"ping -c 3 {h2}")
            socket.send_string(result)

        elif cmd == "exec" and len(parts) >= 3:
            host = mn_api.net.get(parts[1])
            shell_cmd = " ".join(parts[2:])
            result = host.cmd(shell_cmd)
            socket.send_string(result)

        elif cmd == "exit":
            break

        elif cmd == "linkdown" and len(parts) == 3:
            h1 = parts[1]
            h2 = parts[2]
            mn_api.net.configLinkStatus(h1, h2, "down")
            socket.send_string("ok")

        elif cmd == "linkup" and len(parts) == 3:
            h1 = parts[1]
            h2 = parts[2]
            mn_api.net.configLinkStatus(h1, h2, "up")
            # to re-insert the static arp entries
            # TODO: Need to be improved
            mn_api.program_hosts()
            socket.send_string("ok")

        elif cmd == "dumpconn":
            response = str(dumpNetConnections(mn_api.net))
            socket.send_string(response)

        else:
            socket.send_string("❌ Unknown command or invalid arguments")

except KeyboardInterrupt:
    print("🔴 Shutting down Mininet by KeyboardInterrupt")

except Exception as e:
    print(f"❌ Error occurred: {e}")

finally:
    mn_api.stopNetwork()
    print("🛑 Mininet has been shut down!")
