from p4utils.mininetlib.network_API import NetworkAPI
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
print(cur_dir)

net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.setCompiler(p4rt=True)

# Network definition
net.addP4RuntimeSwitch('s1', cli_input=os.path.join(cur_dir, 's1-commands.txt'))
net.setP4Source('s1', os.path.join(cur_dir, 'p4src/l2_basic_forwarding.p4'))

net.addHost('h1')
net.addHost('h2')
net.addHost('h3')
net.addHost('h4')

# set up links
net.addLink('s1', 'h1')
# net.setIntfMac('s1', 'h1', '00:00:00:00:11:01')
# net.setIntfIp('h1', 's1', '10.0.0.1/24')
# net.setIntfMac('h1', 's1', '00:00:00:00:00:01')

net.addLink('s1', 'h2')
# net.setIntfMac('s1', 'h2', '00:00:00:00:11:02')
# net.setIntfIp('h2', 's1', '10.0.0.2/24')
# net.setIntfMac('h2', 's1', '00:00:00:00:00:02')

net.addLink('s1', 'h3')
# net.setIntfMac('s1', 'h3', '00:00:00:00:22:01')
# net.setIntfIp('h3', 's1', '10.0.0.3/24')
# net.setIntfMac('h3', 's1', '00:00:00:00:00:03')

net.addLink('s1', 'h4')
# net.setIntfMac('s1', 'h4', '00:00:00:00:22:02')
# net.setIntfIp('h4', 's1', '10.0.0.4/24')
# net.setIntfMac('h4', 's1', '00:00:00:00:00:04')

# Assignment strategy
net.l2()

# Nodes general options
# net.disablePcapDumpAll()
net.enableLogAll()
net.enableCli()
net.startNetwork()