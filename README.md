# datacenter_ufes
## Repositório para projeto de disciplina de Redes de Datacenter ofertada pelo Programa de Pós Graduação em Engenharia Elétrica.

### Introdução

Este repositório tem como objetivo reunir e organizar uma máquina virtual (VM) para o estudo do Mininet e seus componentes.

O uso do script do Vagrant é opcional. A máquina virtual (VM) planejada tem as seguintes configurações:

(Inserir uma tabela)

### Modo de uso (Vagrant Script):

Faça o download deste repositório e acesse a pasta:


```
git clone
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

Você verá na tela:

(inserir figura)


### Checagem das aplicações:

Esta seção apresenta um roteiro de testes para verificar o funcionamento do Ryu e do Mininet.

Abra dois terminais:

No **terminal 1**, digite o comando abaixo para ativar o controlador Ryu: 
```
ryu-manager ryu.app.simple_switch_stp_13
```

No **terminal 2**, digite o comando abaixo para acessar Mininet:

```
sudo mn --custom ./Code/Fat\ Tree.py --topo=mytopo \
    --controller=remote,ip=127.0.0.1,port=6633 \
    --mac --arp --link=tc
```

Ainda no **terminal 2**, digite os comandos `dump` e `pingall`, para conferir se os dispositivos estão conectados.

Observe se os dois terminais não apresentam erros e se suas informações serão atualizadas com o tempo.

(gif das telas)


Se o comportamento dos logs e dos comandos dentro do Mininet forem semelhantes ao do exemplo acima, a máquina virtual está funcionando como esperado.
