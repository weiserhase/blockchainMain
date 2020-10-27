

from hashlib import sha256
import json
import time

#from flask import Flask, request
import requests
import multiprocessing
import string
import random
#import numba
import os
import time
import sys
from multiprocessing import Pool, Manager
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 4

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()
        self.run = [ self.add_new_transaction,
        self.is_valid_proof,
        self.add_block,
        ]
        #self.initMining()
    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        print('as')
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        print('add')
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def proof_of_work(self, args):
        #args = [block, noce range] 
        #print('proof ' +str(args[1][0]) + ' / ' + str(args[1][1]))
        block = args[0]
        nonce = args[1]# range

        for nonce in range(nonce[0], nonce[1]):
            block.nonce = nonce
            computed_hash = block.compute_hash()
            if(computed_hash.startswith('0' * Blockchain.difficulty)):
                return [computed_hash, nonce]
        return None
    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        self.mine()
    def mine(self):
        start = time.time()
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
        #print(new_block.index)
        #multiprocess proof of work 
        count = 16
        data = []
        with Pool(count) as p:

            n = int(2**32)
            nonce = 0
            nonce_ranges = [
                (nonce + i * n, nonce + (i+1) * n)
                for i in range(count)
            ]
            for nonce in nonce_ranges:
                data.append([new_block, nonce])
            ##################
            print('starting proof')
            reslist = p.imap_unordered(self.proof_of_work, data)
            p.close()
            p.join()
            for res in reslist:
                if(res == None):
                    continue
                #print(res)
                result = res

        print('go on')
        #print(result)
        proof = result[0]
        new_block.nonce = result[1]
        #print(proof, new_block.nonce)
        self.add_block(new_block, proof)
        #print(proof, new_block.nonce)
        self.unconfirmed_transactions = []
        end = time.time()
        
        
        return new_block