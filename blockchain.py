import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        #self.acknowledgements = []
        #self.verified = []
        
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
            response = requests.get(f'http://{node}/chain')

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

        # Reset the current list of transactions (and acknowledgements if implemented)
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

blockchain = Blockchain()
blockchain.new_transaction('ae13114dd2523d23f32','234c23a23e32a23f',{'Name':'John Harvard','Issuing Authority':'Harvard University','Course':'Introduction to Computer Science','Representative':'David J. Malan','Comment':'This is to certify that the applicant successfully completed and received passing grade in the course.'})
print("\n\n Current transactions:",blockchain.current_transactions)
blockchain.new_block('1a3f4561c2b32c1')
print("\nForging a new block...\n\n Chain:",blockchain.chain)
print("\n\n")
