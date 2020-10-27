import time 
import string
import random
import json
import blockchain
blockchain = blockchain.Blockchain()
def id_generator( size=6, chars=string.ascii_uppercase + string.digits+ string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))
    
def newTransaction():
    data = {}
    for i in range(3):
        data[id_generator(5)] = id_generator(5)
    data= {'test': 'test'}
    blockchain.run(json.dumps(data))
    result = getChain()
    return result

def getChain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                    "chain": chain_data})
#print(newTransaction())