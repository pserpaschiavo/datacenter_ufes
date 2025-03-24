from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
import os

class LinuxRouter(Node):
    """Um roteador baseado em Linux com FRR instalado"""
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Habilitar forwarding
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        
    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class FatTreeTopo(Topo):
    def __init__(self, k=4):
        super(FatTreeTopo, self).__init__()
        
        self.k = k
        num_core = (k // 2) ** 2
        num_agg = k * k // 2
        num_edge = num_agg
        num_hosts_per_edge = 2

        # Criação dos dispositivos
        core_switches = [self.addSwitch(f'c{i+1}', cls=OVSKernelSwitch) 
                         for i in range(num_core)]
        agg_switches = [self.addSwitch(f'a{i+1}', cls=OVSKernelSwitch) 
                        for i in range(num_agg)]
        edge_switches = [self.addSwitch(f'e{i+1}', cls=OVSKernelSwitch) 
                         for i in range(num_edge)]
        routers = [self.addHost(f'r{i+1}', cls=LinuxRouter, ip=f'10.0.{i}.1/24') 
                   for i in range(num_edge)]
        
        # Conexões Core-Aggregation
        for i in range(num_core):
            pod_offset = (i // (k//2)) * (k//2)
            for j in range(k//2):
                agg_idx = pod_offset + j
                self.addLink(core_switches[i], agg_switches[agg_idx], 
                            bw=10, intfName1=f'c{i+1}-eth{agg_idx+1}',
                            params1={'ip': f'10.1.{i}.{agg_idx+1}/24'})

        # Conexões Aggregation-Edge
        for i in range(num_agg):
            pod = i // (k//2)
            edge_offset = pod * (k//2)
            for j in range(k//2):
                edge_idx = edge_offset + j
                self.addLink(agg_switches[i], edge_switches[edge_idx], 
                            bw=10, intfName1=f'a{i+1}-eth{edge_idx+1}',
                            params1={'ip': f'10.2.{i}.{edge_idx+1}/24'})

        # Conexões Edge-Routers
        for i in range(num_edge):
            self.addLink(edge_switches[i], routers[i], bw=10,
                         intfName2=f'r{i+1}-eth0',
                         params2={'ip': f'10.0.{i}.1/24'})

        # Conexões Routers-Hosts
        self.hosts = []
        for i in range(num_edge):
            for j in range(num_hosts_per_edge):
                host = self.addHost(f'h{i*num_hosts_per_edge+j+1}',
                                   ip=f'10.0.{i}.{j+2}/24',
                                   defaultRoute=f'via 10.0.{i}.1')
                self.addLink(routers[i], host, bw=10,
                             intfName1=f'r{i+1}-eth{j+1}',
                             params1={'ip': f'10.0.{i}.{j+2}/24'})
                self.hosts.append(host)

def configure_ospf(net, k):
    """Configura o FRR/OSPF em todos os roteadores"""
    # Primeiro garanta que o diretório de configurações existe
    if not os.path.exists('frr_configs'):
        os.makedirs('frr_configs')
    
    # Gerar configurações específicas para cada roteador
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
        
        # Copiar configuração para o container e iniciar FRR
        router.cmd('cp /etc/frr/frr.conf /etc/frr/frr.conf.bak')  # Backup
        router.cmd(f'cp frr_configs/frr_{router.name}.conf /etc/frr/frr.conf')
        router.cmd('systemctl restart frr')
        print(f"Configuração OSPF aplicada em {router.name}")

def run():
    topo = FatTreeTopo(k=4)
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()
    
    # Configurar OSPF
    configure_ospf(net, k=4)
    
    # Testar conectividade
    print("Testando conectividade...")
    net.pingAll()
    
    # Entrar no CLI
    print("Rede Fat-Tree com OSPF+ECMP está funcionando!")
    print("Use 'vtysh' nos roteadores para verificar OSPF")
    net.interact()
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()