import os
import argparse

def generate_frr_configs(k):
    pod = k
    max_paths = k // 2  # ECMP
    num_core = (pod // 2) ** 2
    num_agg = pod * pod // 2
    num_edge = num_agg

    config_dir = "frr_configs"
    os.makedirs(config_dir, exist_ok=True)

    # Limpar configurações antigas
    for f in os.listdir(config_dir):
        os.remove(os.path.join(config_dir, f))

    # Gerar configurações para cada roteador
    for i in range(num_edge):
        config = f"""
hostname r{i+1}
password zebra
enable password zebra

router ospf
 ospf router-id 10.0.{i}.1
 network 10.0.{i}.0/24 area 0
 network 10.1.0.0/16 area 0
 network 10.2.0.0/16 area 0
 maximum-paths {max_paths}
!
line vty
!
"""
        with open(f"{config_dir}/frr_r{i+1}.conf", "w") as f:
            f.write(config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("k", type=int, help="Fat-Tree k parameter")
    args = parser.parse_args()
    generate_frr_configs(args.k)