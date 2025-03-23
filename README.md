# datacenter_ufes
## Repositório para projeto de disciplina de Redes de Datacenter ofertada pelo Programa de Pós Graduação em Engenharia Elétrica.

### **Introdução**

Este repositório tem como objetivo reunir e organizar uma máquina virtual (VM - *Virtual Machine*) para o estudo do *Mininet*, os componentes fundamentais de Redes Definidas por Software (SDN - *Software Defined Networks*), a função dos controladores e a importância das topologias de rede, com um foco especial na topologia *Fat Tree*.

#### Redes Definidas por Software (SDN)

SDN representa um paradigma inovador na área de redes, que propõe a separação do plano de controle do plano de dados. Essa abordagem permite uma gestão de rede mais flexível e programável, facilitando a implementação de serviços e a otimização do desempenho.

#### *Mininet*: Ferramenta de Emulação para Experimentação em SDN

O *Mininet* é uma ferramenta poderosa para a criação de ambientes de rede virtualizados, possibilitando a simulação de topologias complexas e a experimentação com diferentes controladores e aplicações SDN. Sua capacidade de criar redes de forma rápida e eficiente o torna uma ferramenta valiosa para pesquisa e desenvolvimento.

#### Controladores SDN: O Cérebro da Rede

Os controladores SDN desempenham um papel central na arquitetura SDN, sendo responsáveis pelo gerenciamento do fluxo de dados e pela tomada de decisões na rede. Eles se comunicam com os dispositivos de rede através de protocolos como o OpenFlow, permitindo a implementação de políticas de rede de forma centralizada.

#### Topologias de Rede: A Estrutura da Conectividade

A topologia de rede define a forma como os dispositivos estão conectados entre si, influenciando diretamente o desempenho e a confiabilidade da rede. Existem diversas topologias, cada uma com suas próprias características e aplicações.

#### *Fat Tree*: Uma Topologia de Alto Desempenho para Data Centers

A topologia *Fat Tree* se destaca por sua alta largura de banda e baixa latência, tornando-a ideal para data centers e outras aplicações de alto desempenho. Sua estrutura hierárquica e simétrica garante uma distribuição eficiente do tráfego, evitando gargalos e otimizando o desempenho da rede.
Conclusão
___

### **Descrição dos recursos**

O uso do script do Vagrant é opcional. A máquina virtual (VM) planejada tem as seguintes configurações:

|Recursos VM        |Limites        |
|:------------------|--------------:|
|CPU   	            |2 cores   	    |
|Memória	        |4096 Mb        |
|SO   	            |Ubuntu 64bits 	|
|Versão	SO          |22.04 (jammy) 	|
|Versão Python      |3.7.17         |
|Versão	*Mininet*   |2.3.0       	|
|Versão Ryu         |4.34           |
|Versão FRR         |10.3           |


> Caso o usuário prefira usar outro software de virtualização (VirtualBox, VMware, KVM), o arquivo [install_*Mininet*.sh](https://github.com/pserpaschiavo/datacenter_ufes/blob/main/setup_vm/*Mininet*_install.sh) poderá ser usado[^*].
___

---

### **Modo de uso (Vagrant Script)**

Faça o download deste repositório e acesse a pasta:


```
git clone https://github.com/pserpaschiavo/datacenter_ufes.git
cd datacenter_ufes/
```

A seguir:

```
vagrant up
```

Após o término do processo de criação da máquina virtual (VM), digite o comando a seguir para fazer a conexão remota com a VM:

```
vagrant ssh
```

O terminal irá exibir a tela de boas vindas da VM:

![vm_welcome_screen](/assets/images/welcome.png)

___

### **Checagem das aplicações:**

Esta seção apresenta um roteiro de testes para verificar o funcionamento do *Ryu* e do **Mininet**.

Abra dois terminais:

No **terminal 1**, digite o comando abaixo para ativar o controlador *Ryu*: 
```
ryu-manager ryu.app.simple_switch_stp_13
```

No **terminal 2**, digite o comando abaixo para acessar **Mininet**:

```
sudo mn --custom ./Fat-Tree-Data-Center-Topology/Code/Fat\ Tree.py --topo=mytopo \
    --controller=remote,ip=127.0.0.1,port=6633 \
    --mac --arp --link=tc
```

Ainda no **terminal 2**, digite os comandos `dump` e `pingall` para conferir se os dispositivos estão conectados.

Observe se os dois terminais não apresentam erros e se suas informações serão atualizadas com o tempo.

![gif das telas](https://github.com/pserpaschiavo/datacenter_ufes/blob/main/assets/gif/*Mininet*.gif)


> Se o comportamento dos logs e dos comandos dentro do **Mininet** forem semelhantes ao do exemplo acima, a máquina virtual está funcionando como esperado.


[^*]: Após o download do arquivo [install_*Mininet*.sh](https://github.com/pserpaschiavo/datacenter_ufes/blob/main/setup_vm/*Mininet*_install.sh), basta digitar o comando `bash ./datacenter-ufes/setup_vm/*Mininet*_install.sh` em uma pasta que hospedará o *Mininet*.