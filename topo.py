from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController

SCENARIOS = {
    'dual-fiber': (dict(bw=100, delay='5ms'), dict(bw=100, delay='8ms')),
    'eth-wifi': (dict(bw=1000, delay='2ms'), dict(bw=150, delay='12ms')),
    'sat-terr': (dict(bw=50, delay='25ms'), dict(bw=100, delay='180ms')),
    'cellular': (dict(bw=30, delay='35ms'), dict(bw=25, delay='40ms')),
    'adsl': (dict(bw=50, delay='15ms'), dict(bw=10, delay='45ms')),
}
PATHS = [('10.0.1.1', '10.0.1.2'), ('10.0.2.1', '10.0.2.2')]
def build_network(scenario, loss0=0, loss1=0, datapath='kernel'):
    path0, path1 = (dict(p) for p in SCENARIOS[scenario])
    if loss0:
        path0['loss'] = loss0
    if loss1:
        path1['loss'] = loss1

    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    h1 = net.addHost('h1', ip=None)
    h2 = net.addHost('h2', ip=None)
    sA = net.addSwitch('sA', protocols='OpenFlow13', datapath=datapath,
                       dpid='0000000000000001')
    sB = net.addSwitch('sB', protocols='OpenFlow13', datapath=datapath,
                       dpid='0000000000000002')

    net.addLink(h1, sA, intfName1='h1-eth0', **path0)
    net.addLink(h2, sA, intfName1='h2-eth0')
    net.addLink(h1, sB, intfName1='h1-eth1', **path1)
    net.addLink(h2, sB, intfName1='h2-eth1')
    return net, (path0, path1)

def set_addresses(net):
    h1, h2 = net.get('h1', 'h2')
    h1.cmd('ip addr add 10.0.1.1/24 dev h1-eth0')
    h1.cmd('ip addr add 10.0.2.1/24 dev h1-eth1')
    h2.cmd('ip addr add 10.0.1.2/24 dev h2-eth0')
    h2.cmd('ip addr add 10.0.2.2/24 dev h2-eth1')

