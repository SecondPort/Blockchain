# crear una blockchain
# parte 1 - crear una blockchain
#parte 2 - minado de un bloque de la cadena
#importar librerias

import datetime
import hashlib # algoritmos de hashes
import json
from flask import Flask, jsonify

# parte 1
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
    
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1, #genera un indice
                'timestamp' : str(datetime.datetime.now()), #tiempo real
                'proof' : proof, #validacion de la transaccion
                'previous_hash' : previous_hash #hash anterior
        }