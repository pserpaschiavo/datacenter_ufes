# datacenter_ufes
## Repositório para projeto de disciplina de Redes de Datacenter ofertada pelo Programa de Pós Graduação em Engenharia Elétrica.

### Introdução

Este repositório tem como objetivo reunir e organizar uma máquina virtual (VM) para o estudo do Mininet e seus componentes.

O uso do script do Vagrant é opcional. A máquina virtual (VM) planejada tem as seguintes configurações:

|Recursos VM    |Limites        |
|:--------------|--------------:|
|CPU   	        |2 cores   	    |
|Memória	    |4096 Mb        |
|SO   	        |Ubuntu 64bits 	|
|Versão	SO      |22.04 (jammy) 	|
|Versão	Mininet |2.3.0       	|


> Caso o usuário prefira usar outro software de virtualização (VirtualBox, VMware, KVM), o arquivo [install_mininet.sh](https://github.com/pserpaschiavo/datacenter_ufes/blob/main/setup_vm/mininet_install.sh) poderá ser usado[^*].

### Modo de uso (Vagrant Script):

Faça o download deste repositório e acesse a pasta:


```
git clone https://github.com/pserpaschiavo/datacenter_ufes.git
cd datacenter_ufes/
```

A seguir:

```
vagrant up
```

Após o término do processo de criação da máquina virtual (VM), digite:

```
vagrant ssh
```

O terminal irá exibir a tela de boas vindas da VM:

![vm_welcome_screen](/assets/images/welcome.png)


### Checagem das aplicações:

Esta seção apresenta um roteiro de testes para verificar o funcionamento do Ryu e do Mininet.

Abra dois terminais:

No **terminal 1**, digite o comando abaixo para ativar o controlador Ryu: 
```
ryu-manager ryu.app.simple_switch_stp_13
```

No **terminal 2**, digite o comando abaixo para acessar Mininet:

```
sudo mn --custom ./Fat-Tree-Data-Center-Topology/Code/Fat\ Tree.py --topo=mytopo \
    --controller=remote,ip=127.0.0.1,port=6633 \
    --mac --arp --link=tc
```

Ainda no **terminal 2**, digite os comandos `dump` e `pingall` para conferir se os dispositivos estão conectados.

Observe se os dois terminais não apresentam erros e se suas informações serão atualizadas com o tempo.

(gif das telas)


Se o comportamento dos logs e dos comandos dentro do Mininet forem semelhantes ao do exemplo acima, a máquina virtual está funcionando como esperado.


[^*]: Após o download do arquivo [install_mininet.sh](https://github.com/pserpaschiavo/datacenter_ufes/blob/main/setup_vm/mininet_install.sh), basta digitar o comando `bash ./datacenter-ufes/setup_vm/mininet_install.sh` em uma pasta que hospedará o Mininet.