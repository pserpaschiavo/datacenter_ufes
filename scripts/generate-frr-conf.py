import os
import argparse

def generate_frr_configs(k):
    pod = k
    max_paths = k // 2  # ECMP - Número de caminhos iguais
    L1 = (pod // 2) ** 2  # Core
    L2 = pod * pod // 2  # Agregação
    L3 = L2  # Edge

    config_dir = "frr_configs"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Remove arquivos antigos para evitar conflito
    for file in os.listdir(config_dir):
        os.remove(os.path.join(config_dir, file))

    # Configuração para os switches Core
    for i in range(L1):
        switch_id = i + 1
        router_id = f"{switch_id}.{switch_id}.{switch_id}.{switch_id}"
        network = f"10.0.{switch_id}.0/24"
        config = f"""!
router ospf
 ospf router-id {router_id}
 maximum-paths {max_paths}
 network {network} area 0.0.0.0
!
line vty
!
"""
        with open(f"{config_dir}/frr_c{switch_id}.conf", "w") as f:
            f.write(config)

    # Configuração para os switches de Agregação
    for i in range(L2):
        switch_id = L1 + i + 1
        router_id = f"{switch_id}.{switch_id}.{switch_id}.{switch_id}"
        pod_id = i // (pod // 2)  # Identifica a qual pod pertence
        network1 = f"10.0.{pod_id + 1}.0/24"
        network2 = f"10.1.{i + 1}.0/24"
        config = f"""!
router ospf
 ospf router-id {router_id}
 maximum-paths {max_paths}
 network {network1} area 0.0.0.0
 network {network2} area 0.0.0.0
!
line vty
!
"""
        with open(f"{config_dir}/frr_a{switch_id}.conf", "w") as f:
            f.write(config)

    # Configuração para os switches de Borda (Edge)
    for i in range(L3):
        switch_id = L1 + L2 + i + 1
        router_id = f"{switch_id}.{switch_id}.{switch_id}.{switch_id}"
        pod_id = i // (pod // 2)
        network1 = f"10.1.{pod_id + 1}.0/24"
        network2 = f"10.2.{i + 1}.0/24"
        config = f"""!
router ospf
 ospf router-id {router_id}
 maximum-paths {max_paths}
 network {network1} area 0.0.0.0
 network {network2} area 0.0.0.0
!
line vty
!
"""
        with open(f"{config_dir}/frr_e{switch_id}.conf", "w") as f:
            f.write(config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FRR config files for Fat Tree topology")
    parser.add_argument("k", type=int, help="Value of k for Fat Tree topology")
    args = parser.parse_args()

    generate_frr_configs(args.k)
