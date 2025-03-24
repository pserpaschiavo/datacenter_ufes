#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, Node
from mininet.link import TCLink
from mininet.util import dumpNetConnections

# Definição de um roteador Linux que ativa o IP forwarding
class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Ativar o IP forwarding para roteamento
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class MyTopo(Topo):
    def __init__(self):
        super(MyTopo, self).__init__()

        # Definir o valor de k e as quantidades por camada
        k = 4
        pod = k
        L1 = (pod // 2) ** 2     # Número de roteadores Core
        L2 = pod * pod // 2      # Número de roteadores de Agregação
        L3 = L2                # Número de roteadores de Borda (Edge)

        # Criação dos nós de roteamento (LinuxRouter) para todas as camadas
        core = []  # Core
        agg = []   # Agregação
        edge = []  # Edge

        # Adiciona roteadores Core
        for i in range(L1):
            r = self.addNode('c{}'.format(i+1), cls=LinuxRouter)
            core.append(r)

        # Adiciona roteadores de Agregação
        for i in range(L2):
            r = self.addNode('a{}'.format(L1+i+1), cls=LinuxRouter)
            agg.append(r)

        # Adiciona roteadores Edge
        for i in range(L3):
            r = self.addNode('e{}'.format(L1+L2+i+1), cls=LinuxRouter)
            edge.append(r)

        # Criar links entre Core e Agregação
        for i in range(L1):
            core_node = core[i]
            start = i % (pod // 2)
            for j in range(pod):
                agg_node = agg[start + j * (pod // 2)]
                self.addLink(core_node, agg_node, bw=10)

        # Criar links entre Agregação e Edge
        for i in range(L2):
            group = i // (pod // 2)
            for j in range(pod // 2):
                edge_index = group * (pod // 2) + j
                self.addLink(agg[i], edge[edge_index], bw=10)

        # Criar hosts e ligá-los aos roteadores Edge
        for i in range(L3):
            for j in range(2):
                ip_address = "10.2.{}.{}/24".format(i+1, j+2)
                default_route = "via 10.2.{}.1".format(i+1)
                h = self.addHost('h{}'.format(i*2+j+1),
                                 ip=ip_address,
                                 defaultRoute=default_route,
                                 bw=10)
                self.addLink(edge[i], h, bw=10)

topos = { "mytopo": (lambda: MyTopo()) }

def configure_ips(net, topo):
    k = 4
    pod = k
    L1 = (pod // 2) ** 2
    L2 = pod * pod // 2
    L3 = L2

    # Configurar os endereços IP dos roteadores Core
    for i in range(L1):
        router = net.getNodeByName('c{}'.format(i+1))
        # Assumindo que cada roteador core possui 4 interfaces
        for intf in range(1,5):
            router.cmd('ip addr add 10.0.{}.{}0/24 dev c{}-eth{}'.format(i+1, intf, i+1, intf))
            router.cmd('ip link set c{}-eth{} up'.format(i+1, intf))

    # Configurar os roteadores de Agregação
    for i in range(L2):
        router = net.getNodeByName('a{}'.format(L1+i+1))
        for intf in range(1,5):
            router.cmd('ip addr add 10.1.{}.{}0/24 dev a{}-eth{}'.format(i+1, intf, L1+i+1, intf))
            router.cmd('ip link set a{}-eth{} up'.format(L1+i+1, intf))

    # Configurar os roteadores Edge
    for i in range(L3):
        router = net.getNodeByName('e{}'.format(L1+L2+i+1))
        for intf in range(1,5):
            router.cmd('ip addr add 10.2.{}.{}0/24 dev e{}-eth{}'.format(i+1, intf, L1+L2+i+1, intf))
            router.cmd('ip link set e{}-eth{} up'.format(L1+L2+i+1, intf))

    # Instalar FRR e traceroute nos roteadores
    for router in net.controllers + net.switches + net.hosts: 
        # Aqui você pode ajustar se quiser instalar somente nos roteadores
        router.cmd('apt-get update')
        router.cmd('apt-get install -y traceroute frr')
    
    # Iniciar FRR nos roteadores: para cada nó que seja roteador, inicie o FRR com o arquivo de configuração correspondente
    for node in net.controllers + net.switches:
        # Se você tiver arquivos de configuração separados para cada roteador, pode usar:
        node_name = node.name
        node.cmd('frr -d -l stdout -f frr_configs/frr_{}.conf'.format(node_name))
        node.cmd('service frr status')

if __name__ == '__main__':
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    configure_ips(net, topo)
    dumpNetConnections(net.hosts)
    net.interact()
    net.stop()
