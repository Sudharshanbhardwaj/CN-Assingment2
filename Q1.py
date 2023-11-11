from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time

class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class BasicTopo(Topo):
    def build(self, **_opts):
        router1 = self.addNode('R1', cls=LinuxRouter, ip='10.0.1.1/24')
        router2 = self.addNode('R2', cls=LinuxRouter, ip='10.0.2.1/24')
        router3 = self.addNode('R3', cls=LinuxRouter, ip='10.0.3.1/24')

        s1, s2, s3, s4, s5, s6 = [self.addSwitch(s) for s in ('s1', 's2', 's3', 's4', 's5', 's6')]

        # Existing links
        self.addLink(s1, router1, intfName2='R1-eth1', params2={'ip': '10.0.1.1/24'})
        self.addLink(s2, router2, intfName2='R2-eth2', params2={'ip': '10.0.2.1/24'})
        self.addLink(s3, router3, intfName2='R3-eth3', params2={'ip': '10.0.3.1/24'})
        
        # Links for s1
        self.addLink(self.addHost('H1', ip='10.0.1.2/24', defaultRoute='via 10.0.1.1'), s1)
        self.addLink(self.addHost('H2', ip='10.0.1.3/24', defaultRoute='via 10.0.1.1'), s1)
        # Links for s2
        self.addLink(self.addHost('H3', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1'), s2)
        self.addLink(self.addHost('H4', ip='10.0.2.3/24', defaultRoute='via 10.0.2.1'), s2)
        # Links for s3
        self.addLink(self.addHost('H5', ip='10.0.3.2/24', defaultRoute='via 10.0.3.1'), s3)
        self.addLink(self.addHost('H6', ip='10.0.3.3/24', defaultRoute='via 10.0.3.1'), s3)
        
        # Links between routers
        self.addLink(s4, router1, intfName2='R1-eth4', params2={'ip': '10.0.4.1/24'})
        self.addLink(s4, router2, intfName2='R2-eth4', params2={'ip': '10.0.4.2/24'})
        self.addLink(s5, router2, intfName2='R2-eth5', params2={'ip': '10.0.5.1/24'})
        self.addLink(s5, router3, intfName2='R3-eth5', params2={'ip': '10.0.5.2/24'})
        self.addLink(s6, router1, intfName2='R1-eth6', params2={'ip': '10.0.6.1/24'})
        self.addLink(s6, router3, intfName2='R3-eth6', params2={'ip': '10.0.6.2/24'})


def run():
    "Test BasicTopo"
    topo = BasicTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    
    
    net['R1'].cmd('ip route add 10.0.2.0/24 via 10.0.4.2')
    net['R1'].cmd('ip route add 10.0.3.0/24 via 10.0.6.2')

    net['R2'].cmd('ip route add 10.0.1.0/24 via 10.0.4.1')
    net['R2'].cmd('ip route add 10.0.3.0/24 via 10.0.5.2')

    net['R3'].cmd('ip route add 10.0.1.0/24 via 10.0.6.1')
    net['R3'].cmd('ip route add 10.0.2.0/24 via 10.0.5.1')
    
    #For packet capture on Router 1
    R1cap=net['R1'].popen('tcpdump -i any -w R1.pcap')   
    time.sleep(5)
    #Change the default path to the router2
    net['H1'].cmd('ip route add default via 10.0.1.1 nexthop via 10.0.4.2 nexthop via 10.0.5.2 nexthop via 10.0.6.2')
    net.pingAll()
    info('*** Routing Table on Routers:\n')
    print("         Routing Table for Router 1           ")
    info(net['R1'].cmd('route'))
    print("         Routing Table for Router 2           ")
    info(net['R2'].cmd('route'))
    print("         Routing Table for Router 3           ")
    info(net['R3'].cmd('route'))
    
    CLI(net)
    net.stop()
    

if __name__ == '__main__':
    setLogLevel('info')
    run()
