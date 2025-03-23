from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.util import dumpNetConnections

class MyTopo(Topo):
    def __init__(self):
        super(MyTopo, self).__init__()

        # Number of switches per layer
        k = 4
        pod = k
        L1 = (pod // 2) ** 2
        L2 = pod * pod // 2
        L3 = L2

        # Creating switches
        c = []  # core layer switches
        a = []  # aggregation layer switches
        e = []  # edge layer switches

        # Add switches
        for i in range(L1):
            c_sw = self.addSwitch('c{}'.format(i + 1))
            c.append(c_sw)

        for i in range(L2):
            a_sw = self.addSwitch('a{}'.format(L1 + i + 1))
            a.append(a_sw)

        for i in range(L3):
            e_sw = self.addSwitch('e{}'.format(L1 + L2 + i + 1))
            e.append(e_sw)

        # Creating links between switches
        # The core layer and aggregation layer links
        for i in range(L1):
            c_sw = c[i]
            start = i % (pod // 2)
            for j in range(pod):
                self.addLink(c_sw, a[start + j * (pod // 2)], bw=10)

        # aggregation and edge layer links
        for i in range(L2):
            group = i // (pod // 2)
            for j in range(pod // 2):
                self.addLink(a[i], e[group * (pod // 2) + j], bw=10)

        # Creating hosts and adding links between switches and hosts
        for i in range(L3):
            for j in range(2):
                hs = self.addHost('h{}'.format(i * 2 + j + 1), ip=None, bw=10)
                self.addLink(e[i], hs)

topos = {"mytopo": (lambda: MyTopo())}

def configure_ips(net, topo):
    k = 4
    pod = k
    L1 = (pod // 2) ** 2
    L2 = pod * pod // 2
    L3 = L2

    # Configure switch IPs
    for i in range(L1):
        switch = net.getNodeByName('c{}'.format(i + 1))
        switch.cmd('ip addr add 10.0.{}.1/24 dev c{}-eth1'.format(i + 1, i + 1))
        switch.cmd('ip link set c{}-eth1 up'.format(i + 1))
        switch.cmd('ip addr add 10.0.{}.2/24 dev c{}-eth2'.format(i + 1, i + 1))
        switch.cmd('ip link set c{}-eth2 up'.format(i + 1))
        switch.cmd('ip addr add 10.0.{}.3/24 dev c{}-eth3'.format(i + 1, i + 1))
        switch.cmd('ip link set c{}-eth3 up'.format(i + 1))
        switch.cmd('ip addr add 10.0.{}.4/24 dev c{}-eth4'.format(i + 1, i + 1))
        switch.cmd('ip link set c{}-eth4 up'.format(i + 1))

    for i in range(L2):
        switch = net.getNodeByName('a{}'.format(L1 + i + 1))
        switch.cmd('ip addr add 10.1.{}.1/24 dev a{}-eth1'.format(i + 1, L1 + i + 1))
        switch.cmd('ip link set a{}-eth1 up'.format(L1 + i + 1))
        switch.cmd('ip addr add 10.1.{}.2/24 dev a{}-eth2'.format(i + 1, L1 + i + 1))
        switch.cmd('ip link set a{}-eth2 up'.format(L1 + i + 1))
        switch.cmd('ip addr add 10.1.{}.3/24 dev a{}-eth3'.format(i + 1, L1 + i + 1))
        switch.cmd('ip link set a{}-eth3 up'.format(L1 + i + 1))
        switch.cmd('ip addr add 10.1.{}.4/24 dev a{}-eth4'.format(i + 1, L1 + i + 1))
        switch.cmd('ip link set a{}-eth4 up'.format(L1 + i + 1))

    for i in range(L3):
        switch = net.getNodeByName('e{}'.format(L1 + L2 + i + 1))
        switch.cmd('ip addr add 10.2.{}.1/24 dev e{}-eth1'.format(i + 1, L1 + L2 + i + 1))
        switch.cmd('ip link set e{}-eth1 up'.format(L1 + L2 + i + 1))
        switch.cmd('ip addr add 10.2.{}.2/24 dev e{}-eth2'.format(i + 1, L1 + L2 + i + 1))
        switch.cmd('ip link set e{}-eth2 up'.format(L1 + L2 + i + 1))
        switch.cmd('ip addr add 10.2.{}.3/24 dev e{}-eth3'.format(i + 1, L1 + L2 + i + 1))
        switch.cmd('ip link set e{}-eth3 up'.format(L1 + L2 + i + 1))
        switch.cmd('ip addr add 10.2.{}.4/24 dev e{}-eth4'.format(i + 1, L1 + L2 + i + 1))
        switch.cmd('ip link set e{}-eth4 up'.format(L1 + L2 + i + 1))

    # Configure host IPs
    for i in range(L3):
        for j in range(2):
            host = net.getNodeByName('h{}'.format(i * 2 + j + 1))
            new_ip = "10.2.{}.{}/24".format(i + 1, j + 2)
            host.setIP(new_ip, intf="h{}-eth0".format(i * 2 + j + 1))
            host.cmd('ip route add default via 10.2.{}.1'.format(i + 1))

# Install FRR and traceroute and start FRR
    for switch in net.switches:
        switch.cmd('apt-get update')
        switch.cmd('apt-get install -y traceroute frr')
        switch.cmd('frr -d -l stdout -f frr_configs/frr_{}.conf'.format(switch.name))
        switch.cmd('service frr status')

    for host in net.hosts:
        host.cmd('apt-get update')
        host.cmd('apt-get install -y traceroute')
        host.cmd('echo "nameserver 8.8.8.8" > /etc/resolv.conf') #adicionado google dns
        host.cmd('echo "nameserver 8.8.4.4" >> /etc/resolv.conf') #adicionado google dns


if __name__ == '__main__':
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    configure_ips(net, topo)
    net.interact()
    net.stop()