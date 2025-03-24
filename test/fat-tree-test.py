from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info, error
import os
import subprocess

class LinuxRouter(Node):
    """Roteador Linux com FRR para OSPF"""
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        
    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class FatTreeTopo(Topo):
    def __init__(self, k=4):
        super(FatTreeTopo, self).__init__()
        self.k = k
        self.host_list = []  # Lista para armazenar hosts
        self.buildTopology()
    
    def buildTopology(self):
        num_core = (self.k // 2) ** 2
        num_agg = self.k * self.k // 2
        num_edge = num_agg
        num_hosts_per_edge = 2

        # Dispositivos
        cores = [self.addSwitch(f'c{i+1}', cls=OVSKernelSwitch) for i in range(num_core)]
        aggs = [self.addSwitch(f'a{i+1}', cls=OVSKernelSwitch) for i in range(num_agg)]
        edges = [self.addSwitch(f'e{i+1}', cls=OVSKernelSwitch) for i in range(num_edge)]
        routers = [self.addHost(f'r{i+1}', cls=LinuxRouter) for i in range(num_edge)]

        # Conexões Core-Aggregation
        for i, core in enumerate(cores):
            pod = (i // (self.k//2)) * (self.k//2)
            for j in range(self.k//2):
                agg = aggs[pod + j]
                self.addLink(core, agg, bw=10,
                           intfName1=f'c{i+1}-eth{pod+j+1}',
                           params1={'ip': f'10.1.{i}.{j+1}/24'})

        # Conexões Aggregation-Edge
        for i, agg in enumerate(aggs):
            pod = i // (self.k//2)
            for j in range(self.k//2):
                edge = edges[pod * (self.k//2) + j]
                self.addLink(agg, edge, bw=10,
                            intfName1=f'a{i+1}-eth{j+1}',
                            params1={'ip': f'10.2.{i}.{j+1}/24'})

        # Conexões Edge-Router-Hosts
        for i, (edge, router) in enumerate(zip(edges, routers)):
            # Link Edge-Router
            self.addLink(edge, router, bw=10,
                        intfName2=f'r{i+1}-eth0',
                        params2={'ip': f'10.0.{i}.1/24'})
            
            # Hosts
            for j in range(num_hosts_per_edge):
                host = self.addHost(f'h{i*num_hosts_per_edge+j+1}',
                                  ip=f'10.0.{i}.{j+2}/24',
                                  defaultRoute=f'via 10.0.{i}.1')
                self.addLink(router, host, bw=10,
                            intfName1=f'r{i+1}-eth{j+1}',
                            params1={'ip': f'10.0.{i}.{j+2}/24'})
                self.host_list.append(host)
    
    def hosts(self, sort=True):
        """Método exigido pelo Mininet"""
        return sorted(self.host_list, key=lambda h: int(h.name[1:])) if sort else self.host_list

def configure_ospf(net, k):
    """Configura OSPF nos roteadores"""
    os.makedirs('frr_configs', exist_ok=True)
    
    for i, router in enumerate([h for h in net.hosts if 'r' in h.name]):
        config = f"""
hostname {router.name}
password zebra
enable password zebra

router ospf
 ospf router-id 10.0.{i}.1
 network 10.0.{i}.0/24 area 0
 network 10.1.0.0/16 area 0
 network 10.2.0.0/16 area 0
 maximum-paths {k//2}
 passive-interface r{i+1}-eth0
!
line vty
!
"""
        with open(f'frr_configs/frr_{router.name}.conf', 'w') as f:
            f.write(config)
        
        # Configurar interfaces
        router.cmd(f'ip addr add 10.0.{i}.1/24 dev r{i+1}-eth0')
        
        # Configurar FRR
        router.cmd(f'cp frr_configs/frr_{router.name}.conf /etc/frr/frr.conf')
        try:
            subprocess.run(['systemctl', 'restart', 'frr'], check=True)
            info(f'* OSPF configurado em {router.name}\n')
        except subprocess.CalledProcessError as e:
            error(f'* Falha ao reiniciar FRR em {router.name}: {e}\n')

def run():
    setLogLevel('info')
    topo = FatTreeTopo(k=4)
    net = Mininet(topo=topo, link=TCLink, controller=None)
    
    try:
        net.start()
        info('* Configurando OSPF...\n')
        configure_ospf(net, k=4)
        
        info('* Testando conectividade...\n')
        net.pingAll()
        
        info('\n* Comandos úteis:')
        info(' - Nos roteadores: "vtysh" para acessar o shell FRR')
        info(' - "show ip ospf neighbor" para ver adjacências OSPF')
        info(' - "show ip route" para ver rotas ECMP\n')
        
        net.interact()
    finally:
        net.stop()

if __name__ == '__main__':
    run()