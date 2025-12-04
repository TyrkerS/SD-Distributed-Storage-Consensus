import asyncio
from concurrent import futures
import sys
import os
import time
import yaml

from decentralized_nodes import Decentralized_Nodes

# Funció per carregar la configuració dels nodes del yaml
def load_config(file_path):
    # Obrim el fitxer de configuració en mode lectura
    with open(file_path, 'r') as file:
        # Carreguem el fitxer yaml
        config = yaml.safe_load(file)
    return config

async def main():

    # Es carrega la configuració dels nodes
    config = load_config('decentralized_config.yaml')

    # Extraiem la llista de nodes
    nodes = config['nodes']

    # Es crea el primer node
    node_0 = Decentralized_Nodes(nodes[0]['id'], nodes[0]['ip'], nodes[0]['port'])
    node_0.serve()

    # Es crea el segon node
    node_1 = Decentralized_Nodes(nodes[1]['id'], nodes[1]['ip'], nodes[1]['port'])
    node_1.serve()

    # Es crea el tercer node
    node_2 = Decentralized_Nodes(nodes[2]['id'], nodes[2]['ip'], nodes[2]['port'])
    node_2.serve()

    # Afgim les parelles de cada node
    node_0.add_peer(node_1)
    node_0.add_peer(node_2)

    node_1.add_peer(node_0)
    node_1.add_peer(node_2)

    node_2.add_peer(node_0)
    node_2.add_peer(node_1)

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        node_0.server.stop(0)
        node_1.server.stop(0)
        node_2.server.stop(0)

if __name__ == '__main__':
    asyncio.run(main())
    