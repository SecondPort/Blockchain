# crear una criptomoneda
# importar librerias


import datetime
import hashlib  # algoritmos de hashes
import json
from typing import ChainMap
import requests  # para hacer peticiones http
import urllib.parse  # para parsear la url

from flask import Flask, app, jsonify, request
from uuid import uuid4  # generar un identificador unico

# parte 1


class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,  # genera un indice
                'timestamp': str(datetime.datetime.now()),  # tiempo real
                'proof': proof,  # validacion de la transaccion
                'previous_hash': previous_hash, # hash anterior
                'transactions': self.transactions  # transacciones
                }
        self.transactions = []  # limpia las transacciones
        self.chain.append(block)

        return block

    def get_previous_block(self):
        return self.chain[-1]  # devuelve la cadena anterior

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()  # genera un hash
            if hash_operation[:5] == '00000':  # compara el hash con el formato 0000
                check_proof = True
            else:
                new_proof += 1  # si no es igual a 0000, incrementa la prueba
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(
            block, sort_keys=True).encode()  # codifica el bloque
        return hashlib.sha256(encoded_block).hexdigest()  # genera un hash

    def is_chain_valid(self, chain):
        previous_block = chain[0]  # obtiene el primer bloque
        block_index = 1  # indice del bloque actual
        while block_index < len(chain):
            block = chain[block_index]  # obtiene el bloque actual
            # compara el hash del bloque anterior con el hash del bloque actual
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # obtiene la prueba del bloque anterior
            previous_proof = previous_block['proof']
            proof = block['proof']  # obtiene la prueba del bloque actual
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()  # genera un hash
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sende': sender,
                                    'receiver': receiver,
                                    'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urllib.parse.urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes # obtiene la red
        longest_chain = None # cadena mas larga
        max_length = len(self.chain) # longitud de la cadena actual
        for node in network:
            response = requests.get(f'http://{node}/get_chain')# obtiene la cadena de cada nodo
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):# si la longitud es mayor que la actual y es valida
                    max_length = length
                    longest_chain = chain # se actualiza la cadena mas larga
        if longest_chain:
            self.chain = longest_chain # se actualiza la cadena actual
            return True
        return False

# parte 2 minar de un bloque de la cadena




# crear una aplicacion flask
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False;

node_address = str(uuid4()).replace('-', '')  # genera un identificador unico

# crear una blockchain
blockchain = Blockchain()

# Minar un bloque
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()  # obtiene el bloque anterior
    # obtiene la prueba del bloque anterior
    previous_proof = previous_block['proof']
    # genera una prueba de trabajo
    proof = blockchain.proof_of_work(previous_proof)
    # genera un hash del bloque anterior
    previous_hash = blockchain.hash(previous_block)
    # agrega una transaccion
    blockchain.add_transaction(sender=node_address, receiver='Lucas', amount=1)
    block = blockchain.create_block(proof, previous_hash)  # crea un bloque
    response = {'message': 'Congratulations, you just mined block number: {}'.format(block['index']),
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    return jsonify(response), 200  # devuelve un json y un codigo de estado

# validar la cadena de bloques


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(
        blockchain.chain)  # compara la cadena de bloques
    if is_valid:
        response = {'message': 'All good. The blockchain is valid.'}
    else:
        response = {
            'message': 'Houston, we have a problem. The blockchain is not valid.'}
    return jsonify(response), 200

# Obtener la cadena de bloques completa


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,  # devuelve la cadena de bloques
                'length': len(blockchain.chain)}  # devuelve el largo de la cadena
    return jsonify(response), 200



# añadir una nueva transaccion a la cadena de bloques
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'],
                                        json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

# parte 3 desentralizar la blockchain

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# reemplazar la cadena de bloques si es que esa cadena es mas larga
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200



# ejeccutar la aplicacion
app.run(host='0.0.0.0', port=5001)
