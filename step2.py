from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

setLogLevel('info')

net = Mininet(controller=None, switch=OVSSwitch)

h1 = net.addHost('h1', ip=None)
h2 = net.addHost('h2', ip=None)

sA = net.addSwitch('sA', failMode='standalone', dpid='0000000000000001')
sB = net.addSwitch('sB', failMode='standalone', dpid='0000000000000002')

net.addLink(h1, sA, intfName1='h1-eth0')
net.addLink(h2, sA, intfName1='h2-eth0')
net.addLink(h1, sB, intfName1='h1-eth1')
net.addLink(h2, sB, intfName1='h2-eth1')

net.start()

h1.cmd('ip addr add 10.0.1.1/24 dev h1-eth0')
h1.cmd('ip addr add 10.0.2.1/24 dev h1-eth1')
h2.cmd('ip addr add 10.0.1.2/24 dev h2-eth0')
h2.cmd('ip addr add 10.0.2.2/24 dev h2-eth1')

CLI(net)
net.stop()
