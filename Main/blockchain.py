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
        self.chain.append(block) #agrega el bloque a la cadena
        return block

    def get_previous_block(self):
        return self.chain[-1] #devuelve la cadena anterior

    def proof_of_work(self, previous_proof): #validacion de la transaccion
        new_proof = 1 #prueba inicial
        check_proof = False #variable de control
        while check_proof is False: #mientras no se cumpla la validacion
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() #genera un hash
            if hash_operation[:6] == '000000': #compara el hash con el formato 0000
                check_proof = True
            else:
                new_proof += 1 #si no es igual a 0000, incrementa la prueba
        return new_proof #devuelve la prueba

    def hash(self, block): #genera un hash del bloque
        encoded_block = json.dumps( block, sort_keys=True).encode() #codifica el bloque
        return hashlib.sha256(encoded_block).hexdigest() #genera un hash del bloque

    def is_chain_valid(self, chain): #verifica la cadena de bloques
        previous_block = chain[0] #obtiene el primer bloque
        block_index = 1 #indice del bloque actual
        while block_index < len(chain):
            block = chain[block_index] #obtiene el bloque actual
            if block['previous_hash'] != self.hash(previous_block): #compara el hash del bloque anterior con el hash del bloque actual
                return False
            previous_proof = previous_block['proof'] #obtiene la prueba del bloque anterior
            proof = block['proof'] #obtiene la prueba del bloque actual
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest() #genera un hash
            if hash_operation[:6] != '000000':
                return False
            previous_block = block
            block_index += 1
        return True

# parte 2

# crear una aplicacion flask
app = Flask(__name__)
# app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False;


blockchain = Blockchain()

# Minar un bloque

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block() #obtiene el bloque anterior
    previous_proof = previous_block['proof'] #obtiene la prueba del bloque anterior
    proof = blockchain.proof_of_work(previous_proof) #genera una prueba de trabajo
    previous_hash = blockchain.hash(previous_block)#genera un hash del bloque anterior
    block = blockchain.create_block(proof, previous_hash) #crea un bloque
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200 #devuelve un json y un codigo de estado

# validar la cadena de bloques
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain) #compara la cadena de bloques
    if is_valid:
        response = {'message': 'All good. The blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The blockchain is not valid.'}
    return jsonify(response), 200

# Obtener la cadena de bloques completa
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, #devuelve la cadena de bloques
                'length': len(blockchain.chain)} #devuelve el largo de la cadena
    return jsonify(response), 200

# ejeccutar la aplicacion
app.run(host='0.0.0.0', port = 5000)


