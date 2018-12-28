import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = {'192.168.0.5:5000':'address1','192.168.0.5:5001':'address2','192.168.0.5:5002':'address3','192.168.0.5:5003':'address4'}
        self.leader = 1
        
        # Create the genesis block
        self.new_block(previous_hash='1a3f4561c2b32c1')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :return: True if valid, False if not
        """
        
        new_length = len(chain)
        our_length = len(self.chain)
        
        last_block = chain[0]
        current_index = 1
        
        new_valid_block_found = False
        
        # Traverse the chain backwards till a new valid block is found (ignore all other blocks)
        while new_length > our_length:
            if chain[new_length-1]['previous_hash']==self.hash(self.chain[-1]):
                new_valid_block_found = True
                self.chain.append(chain[new_length-1])
                break
            new_length -= 1
        
        if not new_valid_block_found:
            return False
    
        # Verifies the validity of rest of the chain
        while current_index < len(chain):
            block = chain[current_index]
            print('{last_block}')
            print('{block}')
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

        # Grab and verify the chains from all the nodes in our network in order
        
        neighbours = list((self.nodes).keys())
        nodes_len = len(neighbours)
        neighbours_new = []
        
        # Reconfiguring the order of nodes
        for i in range(self.leader,nodes_len):
            neighbours_new.append(neighbours[i])
        for i in range(slef.leader):
            neighbours_new.append(neighbours[i])
        neighbours =neighbours_new
        
        replaced = False
        
        i = self.leader
        for node in neighbours:
            
            # We're only looking for chains longer than ours
            max_length = len(self.chain)
            
            response = requests.get('http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    replaced = True
                    
                    # Update leader status
                    self.leader = i
        
            # Counting leader position
            if(i < nodes_len):
                i+=1
            else:
                i=0

        # Replace our chain if we discovered a new, valid chain longer than ours
        if replaced:
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

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, certificate):
        
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'certificate': certificate,
        })

        return self.last_block['index'] + 1
    
    def verify_transaction():
        # Search in nodes and check if it maps to the address (TASK)
        return False

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        
        #Creates a SHA-256 hash of a Block

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
