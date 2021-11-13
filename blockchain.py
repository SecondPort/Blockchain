# crear una blockchain
# parte 1 - crear una blockchain
# parte 2 - minado de un bloque de la cadena
# importar librerias

import datetime
import hashlib  # algoritmos de hashes
import json
from flask import Flask, app, jsonify

# parte 1


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,  # genera un indice
                 'timestamp': str(datetime.datetime.now()),  # tiempo real
                 'proof': proof,  # validacion de la transaccion
                 'previous_hash': previous_hash  # hash anterior
                 }
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1] #devuelve la cadena anterior
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() #genera un hash
            if hash_operation[:4] == '0000': #compara el hash con el formato 0000
                check_proof = True 
            else:
                new_proof += 1 #si no es igual a 0000, incrementa la prueba
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps( block, sort_keys=True).encode() #codifica el bloque
        return hashlib.sha256(encoded_block).hexdigest() #genera un hash
    
    def is_chain_valid(self, chain):
        previous_block = chain[0] #obtiene el primer bloque
        block_index = 1 #indice del bloque actual 
        while block_index < len(chain):
            block = chain[block_index] #obtiene el bloque actual
            if block['previous_hash'] != self.hash(previous_block): #compara el hash del bloque anterior con el hash del bloque actual
                return False
            previous_proof = previous_block['proof'] #obtiene la prueba del bloque anterior
            proof = block['proof'] #obtiene la prueba del bloque actual
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest() #genera un hash
            if hash_operation[:4] != '0000': 
                return False
            previous_block = block
            block_index += 1
        return True
    
