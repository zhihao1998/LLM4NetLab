import os

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
net.enableCli()

net.startNetwork()

net.stopNetwork()
