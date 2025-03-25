import argparse
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import Controller

# 1. Topologia em Linha
class LinearTopo(Topo):
    def build(self, n=3):
        switches = [self.addSwitch(f's{i+1}') for i in range(n)]
        hosts = [self.addHost(f'h{i+1}') for i in range(n)]
        
        for i in range(n):
            self.addLink(hosts[i], switches[i])
            if i > 0:
                self.addLink(switches[i-1], switches[i])

# 2. Topologia em Árvore
class TreeTopo(Topo):
    def build(self, camadas=2):
        if camadas < 2:
            raise ValueError("A árvore precisa ter pelo menos 2 camadas.")
        
        switches = [self.addSwitch(f's{i+1}') for i in range(camadas)]
        hosts = [self.addHost(f'h{i+1}') for i in range(2**(camadas-1))]
        
        for i in range(1, camadas):
            self.addLink(switches[i-1], switches[i])
        
        for i, host in enumerate(hosts):
            self.addLink(host, switches[-1])

# 3. Topologia em Anel
class RingTopo(Topo):
    def build(self, n=4):
        switches = [self.addSwitch(f's{i+1}') for i in range(n)]
        hosts = [self.addHost(f'h{i+1}') for i in range(n)]
        
        for i in range(n):
            self.addLink(hosts[i], switches[i])
            self.addLink(switches[i], switches[(i+1) % n])  # Conecta em anel

# 4. Topologia em Estrela
class StarTopo(Topo):
    def build(self, n=4):
        central_switch = self.addSwitch('s1')
        hosts = [self.addHost(f'h{i+1}') for i in range(n)]
        
        for host in hosts:
            self.addLink(host, central_switch)

# 5. Topologia em Malha (Mesh)
class MeshTopo(Topo):
    def build(self, n=4):
        switches = [self.addSwitch(f's{i+1}') for i in range(n)]
        hosts = [self.addHost(f'h{i+1}') for i in range(n)]
        
        for i in range(n):
            self.addLink(hosts[i], switches[i])
        
        for i in range(n):
            for j in range(i+1, n):
                self.addLink(switches[i], switches[j])

# Função para rodar o Mininet com uma topologia específica
def run_topology(topo):
    net = Mininet(topo=topo, controller=Controller)
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    print("Escolha a topologia:")
    print("1 - Linha")
    print("2 - Árvore")
    print("3 - Anel")
    print("4 - Estrela")
    print("5 - Malha (Mesh)")
    
    escolha = input("Digite o número da topologia desejada: ")
    
    if escolha == '1':
        n = int(input("Digite o número de nós: "))
        run_topology(LinearTopo(n=n))
    elif escolha == '2':
        camadas = int(input("Digite o número de camadas: "))
        run_topology(TreeTopo(camadas=camadas))
    elif escolha == '3':
        n = int(input("Digite o número de nós: "))
        run_topology(RingTopo(n=n))
    elif escolha == '4':
        n = int(input("Digite o número de nós: "))
        run_topology(StarTopo(n=n))
    elif escolha == '5':
        n = int(input("Digite o número de nós: "))
        run_topology(MeshTopo(n=n))
    else:
        print("Opção inválida. Saindo...")
