import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests

from flask import Flask, jsonify, request

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        #self.acknowledgements = []                                                    # check this! what is this?
        
        # Create the genesis block
        self.new_block(previous_hash='1a3f4561c2b32c1')

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This resolves conflicts by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')                                           #what does this do?

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, previous_hash):
        """
        Create a new Block in the Blockchain
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions (and acknowledgements if implemented)           #see this thing!
        self.current_transactions = []
        #self.acknowledgements = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, certificate):
        
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'certificate': certificate,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        
        #Creates a SHA-256 hash of a Block

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
        
        
# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

#MINERS!
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block

    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",                                                               #what should be this?
        certificate =                                                              # ""
        recipient=node_identifier,
    )

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
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['certificate']) #send this to miners for verification instead

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

'''    
@app.route('/chain', methods=['GET'])
def full_chain():                                                  # do we need this? we need something like given the key extract all the
    response = {                                                     certificates corresponding to it.
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200        
'''        

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


'''
                                                                  IF APPLICABLE    
@app.route('/transactions/ack/new', methods=['POST'])
def acknowledge():
    values = request.get_json()
    sender = values.get('sender')
    recipient = values.get('recipient')
    certificate = values.get('certificate')
    previous_hash = blockchain.chain[-1]['previous_hash']
    acknowledgement = hashlib.sha256((sender+recipient+stocksymbol).encode()).hexdigest()
    blockchain.acknowledgements.append(acknowledgement)
    response = {
        "acknowledgements": blockchain.acknowledgements
    }
    return jsonify(response)
    
@app.route('/transactions/acks', methods=['GET'])
def acknowledgements():
    response = {
        "acknowledgements": blockchain.acknowledgements
    }
    return jsonify(response)    
''' 

 '''      
blockchain = Blockchain()
blockchain.new_transaction('ae13114dd2523d23f32','234c23a23e32a23f',{'Name':'John Harvard','Issuing Authority':'Harvard University','Course':'Introduction to Computer Science','Representative':'David J. Malan','Comment':'This is to certify that the applicant successfully completed and received passing grade in the course.'})
print("\n\n Current transactions:",blockchain.current_transactions)
blockchain.new_block('1a3f4561c2b32c1')
print("\nForging a new block...\n\n Chain:",blockchain.chain)
print("\n\n")
'''



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
