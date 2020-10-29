from hashlib import sha512
import json
import time
import websockets

#from flask import Flask, request
import requests
import multiprocessing
import string
import random
import signal
import os
import time
import random as r
import sys
import asyncio
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


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = int(sys.argv[5])
    def __init__(self, chain, transaction, nonce, difficulty, name):
        self.ch = []
        chain = json.loads(chain)
        for block in chain:
            #block = json.loads(block)
            bl = Block(block['index'], block['transactions'], block['timestamp'], block['previous_hash'], block['nonce'], block['hash'])
            self.ch.append(bl)
        self.chain = self.ch
        self.unconfirmed_transactions = transaction
        self.nonce = nonce
        self.result = []
        self.name = name
        #self.ws = websockets.connect(uri)
        self.new_block = []
        self.mine()
        self.difficulty = int(difficulty)
        #self.initMining()
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def proof_of_work(self, nonce):
        print('proof')
        block = self.new_block
        #print(block.transactions, block.index, block.previous_hash, block.timestamp)
        #nonce = args[0]# range
        #print(nonce)
        for nonce in range(int(nonce[0]), int(nonce[1])):
            block.nonce = nonce
            computed_hash = block.compute_hash()
            s = computed_hash.startswith('0' * Blockchain.difficulty)
            if(s):
                if(self.is_valid_proof(block, computed_hash)):
                    try:
                        asyncio.run(self.submit( block, computed_hash))
                    except KeyboardInterrupt:
                        pass
                    return True
        return None
    async def submit(self,block, hashz):
        #print('submit')
        uri = "ws://" + str(sys.argv[6])
    
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({'type': 'submitShare', 'data':[self.name, [block.__dict__, hashz]]}))
            if(await websocket.recv() == 'true'):
                print('Share Accepted')
    def mine(self):
        print('mine')
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
        count = 16
        n =2**64 /count

        #print(n)
        data = []
        self.new_block = new_block
        for i in range(count):
            data.append( [self.nonce[0] +i*n, self.nonce[0] +(i+1)*n])
        with multiprocessing.Pool(count) as p:
            try:
                reslist = p.map(self.proof_of_work, data )
            except:
                p.terminate()
                p.close()
        for res in reslist:
            if(res == True):
                p.terminate()
                p.close()
        p.join()
            #print(self.result)
                #proof =  self.proof_of_work([new_block, self.nonce])
        #self.result = reslist[r.randint(0, len(reslist)-1)]
        #print(self.is_valid_proof(new_block, self.result[0]))
        
if __name__ == "__main__":
    multiprocessing.freeze_support()
    transaction = (sys.argv[1])
    chain = json.loads(sys.argv[2])
    nonce = [json.loads(sys.argv[3]), json.loads(sys.argv[4])]
    
    difficulty = json.loads(sys.argv[5])
    name = sys.argv[7]
    try:
        blockchain = Blockchain(chain, transaction, nonce, difficulty, name)
    except:
        pass
    #asyncio.run(sendWs())