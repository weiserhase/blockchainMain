import time 
import string
import random
import json
import blockchain as Bl
blockchain = Bl.Blockchain()
if(blockchain.quit == True):
    blockchain = Bl.Blockchain()
Block = Bl.Block
'''
This File is Used to create a link between blockchain.py and miningPool.py 
'''
def getChain():
    '''
    This Function is used to return the Blockchain
    args:
        None
    return:
        Blockchain.__dict__
    toDo:
    '''
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps(chain_data)
def is_valid_proof(block, proof):
    '''
    This Function is used to check if proof is valid
    args:
        block => block
        proof => proof  
    return:
        bool
    toDo:
    '''
    return blockchain.run[1](block, proof)
def add_block(block, proof):
    '''
    This Function is used to add a block to the Blockchain
    args:
        block => block
        proof => proof  
    return:
        bool
    toDo:
    '''
    return blockchain.run[2](block, proof)
#print(newTransaction())
def getDifficulty():
    '''
    This Function is used to get the Blockschains Difficulty
    args:
        None 
    return:
        bool
    toDo:
    '''
    return blockchain.difficulty

