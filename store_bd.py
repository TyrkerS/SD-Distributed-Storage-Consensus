import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + 'proto')
sys.path.append(os.getcwd())

class Store_bd:

    def save(self, key, value):
        # Crear una tabla hash (diccionario)
        hash_table = {}

        # Agregar elementos a la tabla hash
        hash_table[key] = value

        print("s'ha afegit l'element " + value + " amb la clau " + key + " a la base de dades")


    def restore(self):
        pass