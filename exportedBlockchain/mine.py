from hashlib import sha512, sha256
import json
import time
import websockets
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
import concurrent.futures
from numba import jit, cuda 
import config as cfg
class Block:
    '''
    Generate New Block Based on index, transaction, timestamp, previous_hash

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    def __init__(self, index, transactions,  timestamp, previous_hash, nonce = False, has = False ):
        self.index = index
        self.transactions = transactions
        self.timestamp = int(timestamp)
        self.previous_hash = previous_hash
        if(nonce == False):
            self.nonce = 0
        else:
            self.nonce = nonce
        
        #print(self)
        if(has != False):
            #
            self.hash = has
            pass
        else:
            pass
                

    def compute_hash(self):
        '''
        This Function is used to compute the Hash of a block
        args:
            None 
        return:
            bool
        toDo:
        '''
        try:
            block_string = json.dumps(self.__dict__, sort_keys=True)
            if(cfg.config['hash'] == 'sha512' ):
                has = sha512(block_string.encode()).hexdigest()
            elif(cfg.config['hash'] == 'sha256'):
                has =  sha256(block_string.encode()).hexdigest()
            else: 
                has =  sha512(block_string.encode()).hexdigest()
            #self.hash = has
            return has
        except:
            pass


class Blockchain:
    '''
    Generate Blockchain to mine one Block it is reinitialised for every new Job

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    try:
        difficulty = int(sys.argv[5])
    except:
        #print('diff ')
        pass
    def __init__(self, chain, transaction, nonce, difficulty, name):
        self.ch = []
        chain = json.loads(chain)
        for block in chain:
            bl = Block(block['index'], block['transactions'], block['timestamp'], block['previous_hash'], block['nonce'])
            #bl.hash = bl.compute_hash()
            self.ch.append(bl)
        self.kill = False
        self.chain = self.ch
        self.unconfirmed_transactions = transaction
        self.nonce = nonce
        self.result = []
        self.name = name
        self.difficulty = int(difficulty)
        self.new_block = []
        self.mine()  
        self.kill = False
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def isValidProof(self, block, block_hash):
        '''
        This Function is used to check if a block is valid with this proof
        args:
            ~Block 
            block_hash => proof 
        return:
            boolean
        toDo:
            optimize the MinerPool speed #3
        
        '''
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())
    def asyncHelper(self):
        return asyncio.run(self.messageRecv())
    async def messageRecv(self):
        uri = "ws://"+str(sys.argv[6])
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({'type': 'registerWatcher'}))
            async for message in websocket:
                if(message== 'kill'):
                    self.kill = True
                    await websocket.send(json.dumps({'type': 'unregisterWatcher'}))
                    return True

    def proof_of_work(self, nonce):  
        '''
        This Function is used to try out a nonce wich gives a hash with difficulty = (number of leadingZeros) of the hashed block
        args:
            nonce = [border1, border2]  
        return:
            None
            this function sends the data to the Pool
        toDo:
            optimize the way to cancel the MinerPool #2
            optimize the MinerPool speed #3
        '''
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.asyncHelper)
            nz = nonce
            start = time.time()
            block = self.new_block
            for nonce in range(int(nonce[0]), int(nonce[1])):
                if(self.kill == True):
                    exit()
                    return 'kill'
                #if(nonce%3000 == 0):
                    #print('true')
                block.nonce = nonce
                try:
                    computed_hash = block.compute_hash()
                    self.test = block.__dict__
                except:
                    print('0x3')
                if(self.isValidProof(block, computed_hash)):
                    #print(nonce)
                    try:
                        num = nonce - int(nz[0])
                        #submit run the submitFunction
                        asyncio.run(self.submit( block, computed_hash, num))
                    except :
                        print('0x2')
                        pass
                    return [block, computed_hash]
            return None
    async def submit(self,block, hashz, rate):
        '''
        This Function submits a valid block when the proofOfWork function finds a valkid value
        args:
            nonce = [border1, border2]  
        return:
            None
            this function sends the data to the Pool
        toDo:
            optimize the way to cancel the MinerPool #2
            optimize the MinerPool speed #3
        '''
        try:
            uri = "ws://" + str(sys.argv[6])
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({'type': 'submitShare', 'data':[self.name, [block.__dict__, hashz], rate]}))
                return
        except:
            pass
    def mine(self):
        '''
        This Function submits a valid block when the pr
        args:
            nonce = [border1, border2]  
        return:
            None
            this function sends the data to the Pool
        toDo:
            optimize the way to cancel the MinerPool #2
            optimize the MinerPool speed #3
        '''
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash())
        #print('Mining new Block' + str(new_block.index))
        count = multiprocessing.cpu_count()
        n =(self.nonce[1]-self.nonce[0])/count

        data = []
        self.new_block = new_block
        for i in range(count):
            data.append( [self.nonce[0] +i*n, self.nonce[0] +(i+1)*n])
        #try:
        with multiprocessing.Pool(count) as p:
            try:
                #print('test')
                reslist = p.map(self.proof_of_work, data)
            except KeyboardInterrupt:
                p.terminate()
                p.join()
            p.terminate()
            p.join()
            for res in reslist:
                if(res == True):
                    p.terminate()
        #except :
            #print('Failed to run Pool')
            #pass
        p.join()
if __name__ == "__main__":
    #try:
    multiprocessing.freeze_support()
    transaction = (sys.argv[1])
    chain = json.loads(sys.argv[2])
    nonce = [json.loads(sys.argv[3]), json.loads(sys.argv[4])]
    
    difficulty = json.loads(sys.argv[5])
    name = sys.argv[7]
    blockchain = Blockchain(chain, transaction, nonce, difficulty, name)
    #except:
        #print('failed to start the Miner instance')