import asyncio
import threading
import time
import grpc
import sys
import os
from concurrent import futures
import yaml
import concurrent.futures
import pickle

proto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto')
sys.path.append(proto_path)
sys.path.append(os.getcwd())

import store_pb2
import store_pb2_grpc

class Decentralized_Nodes(store_pb2_grpc.KeyValueStoreServicer):

    def __init__(self, node_id, node_ip, node_port):
        self.id = node_id
        self.ip = node_ip
        self.port = node_port
        # Si és el node 0 o el node 2, el pes serà 1, si és el node 1, el pes serà 2
        if (self.id == 0 or self.id == 2):
           self.weight = 1
        elif (self.id == 1):
            self.weight = 2
        # Retard per a l'utilització del slowDown
        self.delay = 0
        # Base de dades interna per a cada node
        self.BD = {}
        # Llista de nodes parelles per enparellar-los quan una opreció no s'executi per falta de pes
        self.peers = []
        # Fitxer de recuperació en cas de que peti amb l'identficador del node
        self.state_file = f'state_node_{self.id}.pkl'
        # En cas de que peti carregarem l'estat directament
        self.load_state()
        self.lock = threading.Lock()

    # Funció per afegir parella al node
    def add_peer(self, peer):
        self.peers.append(peer)

    # Funció per desar l'estat en cas de fallada del node
    def save_state(self):
        # Obrim el fitxer en mode escritura binaria (Fem binaria perque es més ràpid i no tenim la necessitat de llegir el fitxer)
        with open(self.state_file, 'wb') as f:
            # Escribim la informació de la BD del node al fitxer pickle
            pickle.dump(self.BD, f)
        print(f'Estat del node {self.id} desat.')

    # Funció per carregar l'estat en cas de fallada del node
    def load_state(self):
        # Si el fitxer existeix, carreguem l'estat del node
        if os.path.exists(self.state_file):
            # Obrim el fitxer en mode lectura binaria
            with open(self.state_file, 'rb') as f:
                # Carreguem la informació de la BD del node
                self.BD = pickle.load(f)
            print(f'Estat del node {self.id} carregat.')
    
    # Funció per sol·licitar pes a un node
    def request_weight(self, required_weight):
        # Si el pes del node és major o igual al pes requerit, es retorna el pes requerit
        if self.weight >= required_weight:
            # Es resta el pes requerit al pes del node
            self.weight -= required_weight
            # retornem el pes requerit
            return required_weight
        else:
            # En cas contrari, es retorna el pes del node
            weight_available = self.weight
            # Es posa el pes del node a 0
            self.weight = 0
            # Es retorna el pes del node
            return weight_available

    # Funció per afegir una clau i un valor a la base de dades (gRPC)
    def put(self, request, context):
        # Apliquem el retard de l'slowdown
        time.sleep(self.delay)
        # Definim el pes requerit per a executar l'operació
        required_weight = 3

        # Bloquejem el lock perque hem d'editar la BD
        with self.lock:
            # Provem a executar l'operació put de manera local si el node te el propi pes (no passarà mai)
            if self.weight >= required_weight:
                # Es desa el contingut a la base de dades del node
                self.BD[request.key] = request.value
                # Desem l'estat del node per si peta
                self.save_state()
                print(f'Operació put feta correctament al node {self.id}')
                return store_pb2.PutResponse(success=True)
        
        # En cas contrari, es sol·licitarà pes a altres nodes per executar l'operació put
        # Al inici, el pes total acumulat serà el pes del node
        total_weight = self.weight
        # El pes requerit serà el pes requerit (3) menys el pes del node, es el que faltarà per a executar
        required_weight -= self.weight

        # Fem la cerca amb futures per fer-ho alhora de manera asíncrona
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Creem un diccionari de futures amb la crida a la funció request_weight de cada node
            futures = {executor.submit(peer.request_weight, required_weight): peer for peer in self.peers}
            
            # Iterem sobre els futures a mesura que es completen
            for future in concurrent.futures.as_completed(futures):
                # Obtenim el pes del node
                peer_weight = future.result()
                # Acumulem el pes del node al pes total acumulat
                total_weight += peer_weight
                # Restem el pes del node al pes requerit
                required_weight -= peer_weight
                # Si ja tenim suficient pes, sortim del bucle
                if total_weight >= 3:
                    break

        # Si tenim suficient pes, es realitza l'operació put
        if total_weight >= 3:
            # Bloquejem el lock perque hem d'editar la BD
            with self.lock:
                # Es desa el contingut a la base de dades del node
                self.BD[request.key] = request.value
                # Es desa el contingut a la base de dades dels nodes que han ajudat
                for peer in self.peers:
                    # Si el pes del node és major a 0, es desa el contingut a la base de dades del node
                    if peer_weight > 0:
                        # Es desa el contingut a la base de dades del node
                        peer.BD[request.key] = request.value
                # Desem l'estat del node per si peta un cop finalitzada l'operació
                self.save_state()
            print(f'Operació put feta correctament amb ajuda dels nodes al node {self.id}')
            return store_pb2.PutResponse(success=True)
        else:
            # En cas de falla, es retorna un missatge d'error
            print(f"Operació put ha fallat al node {self.id} per falta de pes.")
            return store_pb2.PutResponse(success=False)
        
    # Funció per obtenir el valor d'una clau (gRPC)
    def get(self, request, context):
        # Apliquem el delay de l'slowdown
        time.sleep(self.delay)
        # Definim el pes requerit per a executar l'operació (2)
        required_weight = 2
 
        # Bloquejem el lock perque hem de consultar la BD
        with self.lock:
        # Provem a executar l'operació get de manera local si el node te el propi pes (pot passar en el node_1)
            if self.weight >= required_weight:
                # Es retorna el valor de la clau de la base de dades del node
                value = self.BD.get(request.key, None)
                # Si el valor no és None, es retorna el valor de la clau
                if value is not None:
                    print(f'Operació get feta correctament al node {self.id}, valor: {value}')
                    return store_pb2.GetResponse(value=value, found=True)
                else:
                    # En cas contrari, es retorna un missatge d'error perque la clau no existirà
                    print(f'Operació get ha fallat en el node {self.id} la clau {request.key} no existeix a la base de dades')
                    return store_pb2.GetResponse(value='', found=False)

        # En cas contrari, es sol·licitarà pes a altres nodes per executar l'operació get
        # Al inici, el pes total acumulat serà el pes del node
        total_weight = self.weight
        # El pes requerit serà el pes requerit (2) menys el pes del node, es el que faltarà per a executar
        required_weight -= self.weight

        # Fem la cerca amb futures per fer-ho alhora de manera asíncrona
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Creem un diccionari de futures amb la crida a la funció request_weight de cada node
            futures = {executor.submit(peer.request_weight, required_weight - total_weight): peer for peer in self.peers}
            
            # Iterem sobre els futures a mesura que es completen
            for future in concurrent.futures.as_completed(futures):
                # Obtenim el pes del node
                peer_weight = future.result()
                # Acumulem el pes del node al pes total acumulat
                total_weight += peer_weight
                # Restem el pes del node al pes requerit
                required_weight -= peer_weight
                # Si ja tenim suficient pes, sortim del bucle
                if total_weight >= required_weight:
                    break
        
        # Si tenim suficient pes, es realitza l'operació get
        if total_weight >= required_weight:
            # Bloquejem el lock perque hem de consultar la BD
            with self.lock:
                # Es retorna el valor de la clau de la base de dades del node
                value = self.BD.get(request.key, None)
                # Si el valor no és None, es retorna el valor de la clau
                if value is not None:
                    print(f'Operació get feta correctament amb ajuda dels nodes al node {self.id}, valor: {value}')
                    return store_pb2.GetResponse(value=value, found=True)
                else:
                    # En cas contrari, es retorna un missatge d'error perque la clau no existirà
                    print(f'Operació get ha fallat amb ajuda dels nodes al node {self.id} la clau {request.key} no existeix a la base de dades')
                    return store_pb2.GetResponse(value='', found=False)
        else:
            # En cas de falla, es retorna un missatge d'error
            print(f"Operació get ha fallat al node {self.id} per falta de pes.")
            return store_pb2.GetResponse(value='', found=False)

    # Funció per eliminar una clau de la base de dades (gRPC)
    def slowDown(self, request, context):
        # Apliquem el delay de l'slowdown (Serà l'actual posat per l'usuari)
        time.sleep(request.seconds)
        # Editem la variable interna del node
        self.delay = request.seconds
        print(f'Operació slowDown setejada correctament al node {self.id}')
        return store_pb2.SlowDownResponse(success=True)
    
    # Funció per restaurar el delay de l'slowdown (gRPC)
    def restore(self, request, context):
        # Apliquem el delay de l'slowdown
        time.sleep(self.delay)
        # Restaurem el delay de l'slowdown a 0
        self.delay = 0
        print(f'Operació restore setejada correctament al node {self.id}')
        return store_pb2.RestoreResponse(success=True)

    # Funció per sol·licitar la informació del node (gRPC)
    def quorumRequest(self, request, context):
        # Retornem la informació del node
        return store_pb2.QuorumResponse(id=self.id, ip=self.ip, port=self.port, weight=self.weight)

    # Funció per iniciar el servidor gRPC
    def serve(self):
        # Creem el servidor gRPC
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        # Afegim el servei al servidor
        store_pb2_grpc.add_KeyValueStoreServicer_to_server(self, self.server)
        # Obrim el port del servidor amb les dades del node
        self.server.add_insecure_port(f'{self.ip}:{self.port}')
        # Iniciem el servidor
        self.server.start()
        print(f"Node {self.id} en funcionament a la direcció {self.ip}:{self.port}")


