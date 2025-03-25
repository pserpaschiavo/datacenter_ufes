from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Switch
from mininet.cli import CLI
from mininet.log import setLogLevel
import os

class FRRRouter(Switch):
    """Router baseado no FRRouting."""
    def __init__(self, name, **params):
        super(FRRRouter, self).__init__(name, **params)

    def config(self, **params):
        super(FRRRouter, self).config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd("/usr/lib/frr/frrinit.sh start")

    def terminate(self):
        self.cmd("/usr/lib/frr/frrinit.sh stop")
        super(FRRRouter, self).terminate()

    def start(self, controllers):
        """Inicia o FRR e configura as interfaces."""
        for intf in self.intfs.values():
            self.cmd(f"ip link set {intf} up")
        self.config()

class FatTreeTopo(Topo):
    """Topologia Fat-Tree com OSPF e ECMP usando FRRRouter."""
    def __init__(self, k=4):
        super(FatTreeTopo, self).__init__()
        self.k = k  # Armazena o valor de k para uso posterior
        
        core_switches = []
        agg_switches = []
        edge_switches = []
        hosts = []
        
        # Criando switches Core
        for i in range((k // 2) ** 2):
            core = self.addSwitch(f'c{i+1}', cls=FRRRouter)
            core_switches.append(core)

        # Criando switches Agregação
        for i in range(k * k // 2):
            agg = self.addSwitch(f'a{i+1}', cls=FRRRouter)
            agg_switches.append(agg)
        
        # Criando switches de Borda
        for i in range(k * k // 2):
            edge = self.addSwitch(f'e{i+1}', cls=FRRRouter)
            edge_switches.append(edge)

        # Criando Hosts
        for i in range(k * k):
            host = self.addHost(f'h{i+1}')
            hosts.append(host)

        # Conectando switches Core <-> Agregação
        for i, core in enumerate(core_switches):
            for j in range(k):
                self.addLink(core, agg_switches[j + (i % (k // 2)) * k // 2])
        
        # Conectando switches Agregação <-> Borda
        for i in range(len(agg_switches)):
            pod = i // (k // 2)
            for j in range(k // 2):
                self.addLink(agg_switches[i], edge_switches[pod * (k // 2) + j])
        
        # Conectando Hosts <-> Switches de Borda
        for i in range(len(edge_switches)):
            for j in range(2):
                self.addLink(edge_switches[i], hosts[i * 2 + j])

    def generate_frr_configs(self, net):
        """Gera os arquivos zebra.conf e ospfd.conf com base na topologia."""
        # zebra.conf
        zebra_config = """
hostname zebra
password zebra
enable password zebra
log file /var/log/zebra.log
"""
        ip_base = 10  # IP Base para as sub-redes (10.0.x.x)
        
        for switch in net.switches:
            for intf in net.get(switch).intfs.values():
                ip_address = f"10.0.{ip_base}.{list(net.get(switch).intfs).index(intf) + 1}/24"
                zebra_config += f"interface {intf}\n ip address {ip_address}\n"
        
        with open("/etc/frr/zebra.conf", "w") as f:
            f.write(zebra_config)

        # ospfd.conf
        ospfd_config = """
hostname ospfd
password ospfd
enable password ospfd
log file /var/log/ospfd.log
router ospf
 ospf router-id 0.0.0.1
"""
        for i in range(1, self.k + 1):
            ospfd_config += f" network 10.0.{i}.0/24 area 0\n"

        with open("/etc/frr/ospfd.conf", "w") as f:
            f.write(ospfd_config)

def run():
    topo = FatTreeTopo(k=2)
    net = Mininet(topo=topo, controller=None)
    topo.generate_frr_configs(net)  # Gera os arquivos de configuração do FRR
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
