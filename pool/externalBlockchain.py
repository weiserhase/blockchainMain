import time 
import string
import random
import json
import blockchain
from hashlib import sha512
blockchain = blockchain.Blockchain()
def id_generator( size=6, chars=string.ascii_uppercase + string.digits+ string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))
    
def newTransaction():
    data = {}
    for i in range(3):
        data[id_generator(5)] = id_generator(5)
    data= {'test': 'test'}
    blockchain.run[0](json.dumps(data))
    result = getChain()
    return result

def getChain():
    print('get Chain')
    chain_data = []
    print(blockchain.chain)
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    print(chain_data)
    return json.dumps(chain_data)
def is_valid_proof(block, proof):
    return blockchain.run[1](block, proof)
def add_block(block, proof):
    return blockchain.run[2](block, proof)
#print(newTransaction())

class Block:
    def __init__(self, index, transactions,  timestamp, previous_hash, nonce = False, has = False ):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        if(nonce == False):
            self.nonce = 0
        else:
            self.nonce = nonce
        if(has == False):
            pass
        else:
            self.hash = has
        
        #print(self)

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha512(block_string.encode()).hexdigest()

