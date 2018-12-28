from blockchain import Blockchain
import json
from uuid import uuid4
import requests

from flask import Flask, jsonify, request
        
        
# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

#MINERS!
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200
    
    
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print("\nvalues:",values,"\n")
    # Check that the required fields are in the POST'ed data
    required = ['sender','recipient', 'certificate']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['certificate'])

    response = {'message': 'Transaction will be added to Block {index}'}
    return jsonify(response), 201
   
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200             

@app.route('/transactions/current', methods =['GET'])
def new_transactions():
    if(len(blockchain.current_transactions)!=0):
        transaction = blockchain.current_transactions[-1]
        sender = transaction['sender']
        recipient = transaction['recipient']
        certificate = transaction['certificate']
        response = {
            'sender': sender,
            'recipient': recipient,
            'certificate': certificate,
        }
    else:
        response = {}
    return jsonify(response)

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


blockchain = Blockchain()

"""
blockchain.new_transaction('ae13114dd2523d23f32','234c23a23e32a23f',{'Name':'John Harvard','Issuing Authority':'Harvard University','Course':'Introduction to Computer Science','Representative':'David J. Malan','Comment':'This is to certify that the applicant successfully completed and received passing grade in the course.'})
print("\n\n Current transactions:",blockchain.current_transactions)
blockchain.new_block('1a3f4561c2b32c1')
print("\nForging a new block...\n\n Chain:",blockchain.chain)
print("\n\n")
"""


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
