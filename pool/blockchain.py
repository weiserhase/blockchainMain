

from hashlib import sha512, sha256
import json
import time

import requests
import multiprocessing
import string
import random
import os
import time
import sys
import config as cfg
import mysql.connector as con

class Block:
    '''
    Generate New Block Based on index, transaction, timestamp, previous_hash

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    def __init__(self, index, transactions, timestamp, previousHash, nonce = False):
        self.index = index
        self.transactions = transactions
        self.timestamp = int(timestamp)
        self.previous_hash = previousHash
        if(nonce == False):
            self.nonce = 0
        else:
            self.nonce = nonce
        #self.hash = self.compute_hash()

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
                return sha512(block_string.encode()).hexdigest()
            elif(cfg.config['hash'] == 'sha256'):
                return sha256(block_string.encode()).hexdigest()
            else: 
                return sha512(block_string.encode()).hexdigest()
        except:
            pass

class Blockchain:
    '''
    Generate New Blockchain

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    def __init__(self):
        ''
        self.unconfirmed_transactions = []
        self.chain = []
        self.createGenesisBlock()
        #set these functions in self.run var to call them without await 
        self.run = [ None,
        self.isValidProof,
        self.addBlock,
        ]
        self.difficulty = cfg.config['initDifficulty']
        self.change = False
        self.quit = False
    def createGenesisBlock(self):
        '''
        This Function is used to generate a Genesis Block(initalise the first Block Genesis)
        args:
            None 
        return:
            None
        toDo:
        '''
        
        db = con.connect(
            host= 'localhost',
            user = 'root',
            password = 'mpgsas2020',
            database = 'blockchain'
        )
        cursor = db.cursor()
        sql = 'SELECT ind, data, timestampReal, prevHash, nonce FROM chain'
        cursor.execute(sql)
        data = cursor.fetchall()
        #print(data)
        if(len(data) != 0):
            for i in range(len(data)):
                block = Block(int(data[i][0]),json.loads(data[i][1]), int(data[i][2]), data[i][3], int(data[i][4]))
                self.chain.append(block)
        else:  
            genesis_block = Block(0, [], time.time(), "0")
            block = genesis_block.__dict__
            genesis_block.hash = genesis_block.compute_hash()
            self.chain.append(genesis_block)
            
            sql = 'INSERT INTO chain (ind, data, prevHash, nonce, timestampReal, fee, submitted, timestamp, status, difficulty) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            val = (block['index'], json.dumps(block['transactions']), block['previous_hash'], block['nonce'], block['timestamp'], 0, 'init', time.time(), 'True', cfg.config['initDifficulty'])
            cursor.execute(sql, val)
            db.commit()
            self.quit = True

    @property
    def last_block(self):
        '''
        This Function is used to return the last block in chain 
        args:
            None 
        return:
            ~Block
        toDo:
        '''
        return self.chain[-1]

    def addBlock(self, block, proof):
        '''
        This Function is used to append a Block to Chain 
        args:
            ~Block 
            proof 
        return:
            boolean
        toDo:
        '''
        while(self.change == True):
            pass
        self.change = True
        previous_hash = self.last_block.compute_hash()
        if previous_hash != block.previous_hash:
            print('0x1')
            self.change = False
            
            return False
        if not self.isValidProof(block, proof):
            print('0x2')
            self.change = False
            return False
        #block.hash = proof
        self.chain.append(block)
        self.change = False
        return True

    def isValidProof(self, block, block_hash):
        '''
        This Function is used to check if a block is valid with this proof
        args:
            ~Block 
            block_hash => proof 
        return:
            boolean
        toDo:
        '''
        return(block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())