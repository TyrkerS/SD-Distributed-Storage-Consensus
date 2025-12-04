from concurrent import futures
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + 'proto')
sys.path.append(os.getcwd())

async def main():
    # Es crea el node mestre
    node_master = StorageServiceServicer(True, 0)
    node_master.start_server()

    # Es crea el primer node esclau
    node_slave_1 = StorageServiceServicer(False, 0)
    node_slave_1.start_server()

    # Es crea el segon node esclau
    node_slave_2 = StorageServiceServicer(False, 1)
    node_slave_2.start_server()