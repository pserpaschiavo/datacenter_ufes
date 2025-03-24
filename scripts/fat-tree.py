from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, Node, OVSKernelSwitch
from mininet.link import TCLink
from mininet.util import dumpNetConnections

# Roteador baseado em Linux
class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class FatTreeTopo(Topo):
    def __init__(self):
        super(FatTreeTopo, self).__init__()

        k = 4  # Fator k da Fat-Tree
        num_core = (k // 2) ** 2
        num_agg = k * k // 2
        num_edge = num_agg
        num_hosts_per_edge = 2

        core_switches = []
        agg_switches = []
        edge_switches = []
        routers = []
        hosts = []

        # Adiciona switches Core
        for i in range(num_core):
            switch = self.addSwitch(f'c{i+1}', cls=OVSKernelSwitch)
            core_switches.append(switch)

        # Adiciona switches Agregação
        for i in range(num_agg):
            switch = self.addSwitch(f'a{i+1}', cls=OVSKernelSwitch)
            agg_switches.append(switch)

        # Adiciona switches Edge
        for i in range(num_edge):
            switch = self.addSwitch(f'e{i+1}', cls=OVSKernelSwitch)
            edge_switches.append(switch)

        # Adiciona roteadores na camada Edge
        for i in range(num_edge):
            router = self.addHost(f'r{i+1}', cls=LinuxRouter)
            routers.append(router)
            self.addLink(router, edge_switches[i], bw=10)

        # Conectar Core a Agregação (Corrigido)
        for i in range(num_core):
            for j in range(k // 2):
                agg_index = (i // (k // 2)) * (k // 2) + j
                self.addLink(core_switches[i], agg_switches[agg_index], bw=10)

        # Conectar Agregação a Edge
        for i in range(num_agg):
            for j in range(k // 2):
                self.addLink(agg_switches[i], edge_switches[(i // (k // 2)) * (k // 2) + j], bw=10)

        # Criar Hosts e conectar aos switches Edge
        for i in range(num_edge):
            for j in range(num_hosts_per_edge):
                host = self.addHost(f'h{i*num_hosts_per_edge + j + 1}', ip=f'10.0.{i}.{j+2}/24', defaultRoute=f'via 10.0.{i}.1')
                hosts.append(host)
                self.addLink(edge_switches[i], host, bw=10)

topos = {"fattree": (lambda: FatTreeTopo())}

if __name__ == '__main__':
    topo = FatTreeTopo()
    net = Mininet(topo=topo, link=TCLink, controller=RemoteController)
    
    net.start()

    # Configurar roteadores após iniciar a rede
    for router in net.hosts:
        if 'r' in router.name:  # Verifica se é um roteador
            router.cmd('sysctl -w net.ipv4.ip_forward=1')
            router.cmd('ip route add default via 10.0.0.1')

    dumpNetConnections(net)  # Corrigido

    net.interact()
    net.stop()
