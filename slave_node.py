import threading
import time
import grpc
import sys
import os
from concurrent import futures
import concurrent.futures
import pickle

proto_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto')
sys.path.append(proto_path)
sys.path.append(os.getcwd())

import store_pb2
import store_pb2_grpc


class SlaveNode(store_pb2_grpc.KeyValueStoreServicer):
    def __init__(self, master_address):
        self.data = {}  # Almacenamiento clave-valor
        self.master_address = master_address
        self.is_master = False
        self.register_with_master()

    def put(self, request, context):
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
        context.set_details('Only master can handle put requests')
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

    def canCommit(self, request, context):
        return CanCommitResponse(canCommit=True)

    def doCommit(self, request, context):
        self.data[request.key] = request.value
        return DoCommitResponse(success=True)

    def abort(self, request, context):
        return AbortResponse(success=True)

    def register_with_master(self):
        with grpc.insecure_channel(self.master_address) as channel:
            stub = KeyValueStoreStub(channel)
            response = stub.registerNode(RegisterNodeRequest(nodeAddress=f"localhost:{self.port}"))
            if not response.success:
                print("Failed to register with master")

    def serve(self, port):
        self.port = port
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_KeyValueStoreServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"SlaveNode listening on port {port}")
        server.wait_for_termination()
