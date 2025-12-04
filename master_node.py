import threading
import time
import grpc
import sys
import os
from concurrent import futures
import concurrent.futures
import pickle
# En documento1

# Importar pinga desde proto
from proto import store_pb2
from proto import store_pb2_grpc

proto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto')
sys.path.append(proto_path)
sys.path.append(os.getcwd())

import store_pb2
import store_pb2_grpc

class MasterNode(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self):
        self.nodes = []  # Lista de nodos esclavos
        self.data = {}   # Almacenamiento clave-valor
        self.is_master = True

    def put(self, request, context):
        can_commit = all(self.can_commit(node, request) for node in self.nodes)
        if can_commit:
            self.do_commit(request)
            return PutResponse(success=True)
        else:
            self.abort(request)
            return PutResponse(success=False)

    def get(self, request, context):
        value = self.data.get(request.key, None)
        return GetResponse(value=value, found=(value is not None))

    def slowDown(self, request, context):
        time.sleep(request.seconds)
        return SlowDownResponse(success=True)

    def restore(self, request, context):
        return RestoreResponse(success=True)

    def heartbeat(self, request, context):
        return HeartbeatResponse(alive=True)

    def register_node(self, request, context):
        self.nodes.append(request.nodeAddress)
        return RegisterNodeResponse(success=True)

    def can_commit(self, node, request):
        with grpc.insecure_channel(node) as channel:
            stub = KeyValueStoreStub(channel)
            response = stub.canCommit(CanCommitRequest(key=request.key, value=request.value))
            return response.canCommit

    def do_commit(self, request):
        self.data[request.key] = request.value
        for node in self.nodes:
            with grpc.insecure_channel(node) as channel:
                stub = KeyValueStoreStub(channel)
                stub.doCommit(DoCommitRequest(key=request.key, value=request.value))

    def abort(self, request):
        for node in self.nodes:
            with grpc.insecure_channel(node) as channel:
                stub = KeyValueStoreStub(channel)
                stub.abort(AbortRequest(key=request.key))

    def serve(self, port):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_KeyValueStoreServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"MasterNode listening on port {port}")
        server.wait_for_termination()
