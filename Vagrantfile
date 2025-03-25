Vagrant.configure("2") do |config|
    config.vm.define "mininet" do |mininet|
        mininet.vm.box = "ubuntu/jammy64"
        mininet.vm.hostname = "mininet"
        mininet.vm.network "private_network", ip: "172.89.0.11"
        #mininet.vm.network "public_network", type: "dhcp"

        mininet.ssh.insert_key = false
        mininet.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa']
        mininet.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/authorized_keys"

        mininet.vm.provision :shell, privileged: false, :path => "setup_vm/mininet_install.sh"

        mininet.vm.provider "virtualbox" do |vb|
            vb.gui = false
            vb.cpus = 2
            vb.memory = "4096"  
        end
    end
end

