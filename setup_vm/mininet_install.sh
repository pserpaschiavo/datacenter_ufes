#!/bin/bash

# Atualizar e instalar pacotes necessários
sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install vim git python-is-python3 software-properties-common python3.7-full python3.7-venv -y
sudo apt upgrade -y

# Clonar e configurar o Mininet
git clone https://github.com/mininet/mininet.git
cd mininet
git checkout -b mininet-2.3.0 2.3.0

# Corrigir URLs no script de instalação
sed -i.bak 's|git://|https://|g' ./util/install.sh

# Instalar o Mininet
./util/install.sh -a

# Instalar o FRR - FRRouting
curl -s https://deb.frrouting.org/frr/keys.gpg | sudo tee /usr/share/keyrings/frrouting.gpg > /dev/null

FRRVER="frr-stable"
echo deb '[signed-by=/usr/share/keyrings/frrouting.gpg]' https://deb.frrouting.org/frr \
     $(lsb_release -s -c) $FRRVER | sudo tee -a /etc/apt/sources.list.d/frr.list

sudo apt update && sudo apt install frr frr-pythontools

# Criar e ativar o ambiente virtual
python3.7 -m venv /home/vagrant/.venv
source /home/vagrant/.venv/bin/activate

python -V

# Instalar as bibliotecas no ambiente virtual
pip install ryu==4.34 eventlet==0.30.2

pip list

# Configurar o PATH e ativar o ambiente virtual no .bashrc
echo 'source /home/vagrant/.venv/bin/activate' >> /home/vagrant/.bashrc
echo 'export PATH=$PATH:~/.local/bin' >> /home/vagrant/.bashrc

# Clonar o repositório datacenter-ufes
git clone https://github.com/pserpaschiavo/datacenter_ufes.git

rm -rf ./datacenter_ufes/assets 
rm -rf ./datacenter_ufes/setup_vm 
rm -rf ./datacenter_ufes/.gitignore 
rm -rf ./datacenter_ufes/Vagrantfile

# Recarregar o .bashrc para aplicar as alterações
source /home/vagrant/.bashrc

echo "Tudo Pronto. Bons Estudos!!!"