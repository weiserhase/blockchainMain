import json
import blockchain
import subprocess
import externalBlockchain
import asyncio
import time
import numpy as np
from decimal import *
import hashlib
import requests
import math
import sys
import mysql.connector as con
import os

from conversion import Conversion as cv
class MiningPool:
    ''' 
    This class is the MiningPool class it handles all statistics, transactions and all data submited to the Pool from any instance 

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    def __init__(self):
        ''' This Function Initialises the MiningPool and sets all vars '''
        #Initialise Mining Pool with all needed variables
        self.openTransactions = []
        self.openJobs = []
        self.miners = {}
        self.jobsize = 0
        self.blockchain = externalBlockchain.blockchain
        self.rewards = {}
        self.totalHashingPower = 1
        self.start = 0
        self.submitted = []
        self.interrupt = False
        self.timings = []
        self.validBlock = self.blockchain.last_block.index +1
        self.suspendedMiners = {}
        self.bundledTransactions = []
        self.chainData = []
        self.watchers = []
        self.cv = cv()
        self.db = con.connect(
            host= cfg.config['dbHost'],
            user = cfg.config['dbUser'],
            password = cfg.config['dbPassword'],
            database = cfg.config['dbDatabaseName']
        )
        self.cursor = self.db.cursor()
        self.reinitialiseMiners()
    #Pool Functions

    def bundleTransactions(self):
        '''This Functions Bundles Transactions in Chunks with the size Specified in the Config File
        args:
            None
        return:
            None
        toDo:
            Done~Sort Jobs by Fee #1
        '''
        size = self.cv.byteConversion(cfg.config['blockSize'], cfg.config['blockSizeUnit'], 'b') 
        transactionCollection = []
        fee = 0
        #Append Transactions to bundledTransactions 
        for i in range(len(self.openTransactions)):
            transaction = self.openTransactions[i]
            transactionCollection.append(transaction)
            #if check if the collection is big enough
            if(sys.getsizeof(transactionCollection) >= size):
                for transact in transactionCollection:
                    try:
                        fee += transact['fee']
                    except:
                        pass
                self.bundledTransactions.append([fee,transactionCollection])
                transactionCollection = []

                fee = 0
            elif(i == len(self.openTransactions)-1):
                for transact in transactionCollection:
                    try:
                        fee += transact['fee']
                    except:
                        pass
                self.bundledTransactions.append([fee,transactionCollection])

        self.openTransactions = []


    async def generateNewJob(self):
        '''This Function Generates new Jobs for every registered Miner and sends the Job to them´
        args:
            None
        return:
            {}
        toDo:
            Done~Sort Jobs by Fee #1
        '''
        #Generate New Jobs 
        self.openJobs = []
        self.bundleTransactions()
        self.bundledTransactions = sorted(self.bundledTransactions, key=lambda k: k[0], reverse=True)
        #check if there is a new Transaction in Queue
        if(len(self.bundledTransactions) == 0):
            #dont send a new Job to The Miners if there is no job 
            return False
        if(len(self.miners) == 0):
            return False
        #sort Transaction based on fee
        if(cfg.config['hash'] == 'sha256'):
            ha = hashlib.sha256('test'.encode()).hexdigest
        elif(cfg.config['hash'] == 'sha512'):
            ha = hashlib.sha512('test'.encode()).hexdigest
            ha = str(ha)
        ma = 2**len(ha)
        perMiner = ma/len(self.miners)
        data = []
        #create data for each miner
        print('Job created with Index: '+ str(self.blockchain.last_block.index +1)+ ' and Difficulty: ' + str(self.blockchain.difficulty))
        print(str(len(self.bundledTransactions)) +' Blocks are in queue with a size of bytes ' +str(self.cv.byteConversion(sys.getsizeof(str(self.bundledTransactions)), 'b', 'kb')) +'kb with a size of ' + str(self.cv.byteConversion(sys.getsizeof(str(self.bundledTransactions[0])), 'b', 'kb') )+'kb')
        for i in range(len(self.miners)):
            start = i*perMiner
            data.append([self.bundledTransactions[0][1], json.dumps([self.blockchain.last_block.__dict__]), start,  start+ perMiner, self.blockchain.difficulty, cfg.config['hash']])
        self.openJobs = data 
        self.chainData = [self.bundledTransactions[0][1], json.dumps(self.blockchain.last_block.__dict__)]
        self.start = time.time()
        #send Data to Miners 
        for index in range(len(self.openJobs)):
            await( list(self.miners.values())[index][0].send(json.dumps({'type':'newJob', 'data' :data[index]})))
        for watcher in self.watchers:
            await watcher.send(json.dumps('kill'))
    def reinitialiseMiners(self):
        '''This Function Initialises Miners that were registered and saved to db
        args:
            None
        return:
            None
        toDo:
            None
        '''
        sql = 'SELECT  name, hashrate, acceptedShares, rejectedShares, payout FROM miners '
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        for miner in data:
            #print(miner)
            if(miner[0]in self.suspendedMiners.keys()):
                continue
            self.suspendedMiners[miner[0]] = ['websocketObject', [int(miner[2]),int(miner[3]),float(miner[1]), time.time(), [float(miner[1]) ]]]
            self.rewards[miner[0]] = float(miner[4])
    async def registerMiner(self, args, websocket):
        '''This Function Registers Miners on Mining Pool and sends them a new Job when they are registered
        
            stat array = [shares, rejected , hashrate, registered, hashrate list]
        args:
            args => Socketserver 'data' {
                'name' => minerName
                'hashrate' => 'minerHashrate'
            }
            websocket => The Websocket Instance of the Miner 
        return:
            {}
        toDo:
            None
        '''
        sql = 'SELECT  name, hashrate, acceptedShares, rejectedShares, payout FROM miners WHERE name = %s'
        values= [args['name']]
        self.cursor.execute(sql, values)
        data = self.cursor.fetchall()
        if args['name'] in self.suspendedMiners.keys():
            self.miners[args['name']]  = self.suspendedMiners[args['name']]
            self.miners[args['name']][0] = websocket
            del self.suspendedMiners[args['name']]
            print('miner "'+str(args["name"]) +'" reregistered mining with a hashrate of: ' +str(args['hashrate']/1e6) +str("MHash"))
            if(self.openJobs == []):
                await self.generateNewJob()
                if(self.openJobs != []):
                    await websocket.send(json.dumps({'type':'newJob', 'data':self.openJobs[0]}))
                return {'type': 'exit'}
            else:
                #send Job to Miner
                await websocket.send(json.dumps({'type':'newJob', 'data':self.openJobs[0]}))
        elif(len(data) == 0):
            self.rewards[args['name']] = 0
            self.miners[args['name']] = ([websocket, [0,0,args['hashrate'], time.time(), []]])
            #calculate the Total Hashing Power of the Pool
            for miner in self.miners:
                self.totalHashingPower += args['hashrate']
            print('miner "'+str(args["name"]) +'" registered mining with a hashrate of: ' +str(args['hashrate']/1e6) +str("MHash"))
            sql = 'INSERT INTO miners (name, hashrate, acceptedShares, rejectedShares, payout, registered, status, currentStatus, password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            val = (args['name'], args['hashrate'], 0, 0, 0, time.time(), json.dumps(['active']), 'active', '')
            self.cursor.execute(sql, val)
            self.db.commit()
            if(self.openJobs == []):
                await self.generateNewJob()
                return {'type': 'exit'}
            else:
                #send Job to Miner
                await websocket.send(json.dumps({'type':'newJob', 'data':self.openJobs[0]}))
        else:
            raise Exception('miner cannot be registered')
    async def suspendedMiner(self, name):
        try:
            self.suspendedMiners[name] = self.miners[name]
            del self.miners[name]
        except:
            pass
    async def submitShare(self, args):
        '''
        The Function Accepts or Declines Shares submitted by a Miner
        This Function Uses Old Syntax and must be rewritten in the future 
        args:
            args = message 'data' {
                0 => str minerName
                1 =>[
                    0 => block.__dict__ 
                    1 => str proofOfWork 
                ]
            }
        return:
            {}
        toDo:
            Use Fee instead of unified Reward #1
        '''
        #submit Share to Pool
        #print('sub')
        while(self.interrupt == True):
            pass
        block = (args[1][0])
        
        #if this block has already been submitted
        if(block['index'] in self.submitted):
            ac = 'Declined'
            data ={'type':'share' , 'data':{'status': ac, 'index':self.validBlock , 'accepted':self.miners[args[0]][1][0], 'rejected':self.miners[args[0]][1][1]}}
            await (self.miners[args[0]][0].send(json.dumps(data)))
            return{}

        #Regenerate the Block submitted by miner
        Block = externalBlockchain.Block(block['index'], block['transactions'], block['timestamp'], block['previous_hash'], block['nonce'])
        ch = (externalBlockchain.add_block(Block, args[1][1]))
        
        #check if the block is valid
        if(ch  == True and Block.index == self.validBlock):
            #if share is valid
            ac = 'Accepted'
            self.submitted.append(Block.index)
            self.openJobs = []
            self.submitted.append(Block.index)
            self.miners[args[0]][1][0]  = 1 + self.miners[args[0]][1][0]

            #calculate the miners hashrate

            
            delta = time.time()-self.start
            
            self.miners[args[0]][1][4].append((args[2]*16)/delta)
            c = cfg.config['lastHashes']
            total = 0
            div = 0
            for i in range(c):
                try:
                    total += self.miners[args[0]][1][4][-i]
                    div +=1 
                except:
                    pass
            self.miners[args[0]][1][2] = total/div
            #print(total, c)
            
            #Generate total Hashingpower
            self.totalHashingPower = 0
            for name in list(self.miners.keys()):
                #print(self.miners[name][1][2])
                self.totalHashingPower = self.totalHashingPower + self.miners[name][1][2]

            #Reward Miner for mined Block
            #Implement Fee
            for name in list(self.miners.keys()):
                self.rewards[name] = self.rewards[name] +((self.miners[name][1][2])/self.totalHashingPower) * self.bundledTransactions[0][0]
            
            name = args[0]
            print('Share Accepted by ' +str(args[0]) +' Index: ' +str(Block.index) +' HashingPower: '+str(self.miners[name][1][2]) +' Total Payout: ' + str(self.rewards[name]), end='\n')
            
            #Calculate new Difficulty
            #The Difficulty is calculated based on the last 10(conf) submitted blocks
            #Difficulty should be arround 
            tfeb = 30 #time for every block in s
            lastdiff = self.blockchain.difficulty
            diff = math.log((1 /(self.totalHashingPower*tfeb)), (1/16))
            tfeb = 1/((1/16)**self.blockchain.difficulty*self.totalHashingPower) 
            delta = time.time()-self.start
            if(Block.index%1 == 0):
                if((tfeb - delta) > (tfeb*0.4)):
                    self.blockchain.difficulty = self.blockchain.difficulty + 1
                    
            if((tfeb - delta) < (-tfeb*0.2) and self.blockchain.difficulty > 1):
                self.blockchain.difficulty =  self.blockchain.difficulty - 1
            self.blockchain.difficulty = int(round(diff, 0))
            #Generate new Work with new Block index
            self.validBlock = self.validBlock + 1
            ##############
            #Insert Data in db
            
            #Block = externalBlockchain.Block(block['index'], block['transactions'], block['timestamp'], block['previous_hash'], block['nonce'])   
            #########
            
            sql = "UPDATE miners SET hashrate = %s, acceptedShares = %s, rejectedShares= %s, payout = %s WHERE name = %s"
            val = (self.miners[name][1][2], self.miners[name][1][0], self.miners[name][1][1], self.rewards[name], name)
            self.cursor.execute(sql, val)
            self.db.commit()
            sql = 'INSERT INTO chain (ind, data, prevHash, nonce, timestampReal, fee, submitted, timestamp, status, difficulty) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            val = (block['index'], json.dumps(block['transactions']), block['previous_hash'], block['nonce'], block['timestamp'], self.bundledTransactions[0][0], name, time.time(), 'True', lastdiff)
            self.cursor.execute(sql, val)
            self.db.commit()
            
            del self.bundledTransactions[0]
            await self.generateNewJob()
        else:

            #if share is invalid
            ac = 'Declined'
            self.miners[args[0]][1][1]  += 1
            self.miners[args[0]][1][4].append(args[2])
        data ={'type':'share' , 'data':{'status': ac, 'index':self.validBlock , 'accepted':self.miners[args[0]][1][0], 'rejected':self.miners[args[0]][1][1]}}
        self.timings.append(time.time()-self.start)
        
        await (self.miners[args[0]][0].send(json.dumps(data)))
        return {}
    async def newTransaction(self, args):
        '''
        This Function is used to submit a new Transaction to the Pool 
        This Transaction takes the last position in queue but in future Versions of this Blockchain you will be able to submit a Transaction Fee so the Poll will sort queue based on the Fee the Transaction has and the Reward will be the divided Fee
        args:
            args => [Message 'data' {
                *
                future 'fee' => int fee
            }, multiple messages accepted]
        return:
            Blockchain.__dict__
        toDo:
            Done ~ Use Fee instead of unified Reward #1 
        '''
        #Submit new Transactions
        for transaction in args:
            self.openTransactions.append(transaction)
        if(self.openJobs == []):
            await self.generateNewJob()
        return externalBlockchain.getChain()
    
    async def getChain(self):
        '''
        this Function is used to get the current Blockchain
        args:
            None
        return:
            Blockchain.__dict__
        toDo:
            None
        '''
        return externalBlockchain.getChain()

        

class Handler:
    ''' 
    This class handels socketServer requests and call the functions by the type submited in message

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    def __init__(self):
        self.miningPool = MiningPool()
    async def main(self , message, websocket):
        '''
        this Function is used to handle handle the messages by type in message
        args:
            message #submitted to websocketServer
            ~websocket
        return:
            ~  #no json.dumps
        toDo:
            None
        '''
        message = json.loads(message)
        #frontend calls
        if(message['type'] == "getChain"):
            result = {'type': 'chainData', 'data':await self.miningPool.getChain()}
            return result
        if(message['type'] =='getMinerData'):
            result = {'type': 'minerData', 'data':[self.miningPool.miners , self.miningPool.suspendedMiners]}
            return result
        if(message['type'] == 'getGlobalStats'):
            data = {'totalHashingPower': self.miningPool.totalHashingPower}
            result = {'type': 'globalStats', 'data':data}
        #Watcher/Listeners
        if(message['type'] == "registerWatcher"):
            result = self.miningPool.watchers.append(websocket)
            return result
        if(message['type'] == "unregisterWatcher"):
            result = self.miningPool.watchers.remove(websocket)
            return result
        
        if(message['type'] == "getData"):
            result = self.miningPool.chainData
            return result
        #Miners 
        args = message['data']
        if(message['type'] == "registerMiner"):
            result = await self.miningPool.registerMiner((args), websocket)
            return result
        if(message['type'] == "submitShare"):
            result = await self.miningPool.submitShare((args))
            return result
        if(message['type'] == "newTransaction"):
            result = await self.miningPool.newTransaction(args)
            return result
        if(message['type'] == "getTimings"):
            result = self.miningPool.timings
            return result

import websockets
import asyncio 

#main loop to establish the websocketServer
#set connections as global Var
connections = list()
#initialise Handler
handler = Handler()
async def handleClient(websocket, path):
    '''
    this Function is used to handle new Incoming Messages
    args:
        ~websocket
        path #path wich the websocket  
    return:
    None
    toDo:
        None
    '''
    name = ''
    try:
        connections.append(websocket)
        async for message in websocket:
            #does this coroutine every time a message arrives
            if(json.loads(message)['type'] == "disconnect"):
                connections.remove(websocket)
                await handler.miningPool.suspendedMiner(name)
                return
            result = await handler.main(message, websocket)
            try:
                name = result['name']
            except:
                pass
            if(result != {}):
                await websocket.send(json.dumps(result))
        connections.remove(websocket)
        await handler.miningPool.suspendedMiner(name)
    except Exception as e:
        if(name != ''):
            print('canceling Connection to '+ str(name), ' |Exception :' +str(e))
            #if connection closes abnormaly 
            connections.remove(websocket)
            await handler.miningPool.suspendedMiner(name)
            return
        else:
            #print('canceling Connection because of Exception :' +str(e))
            return
    

async def debug(websocket, path):
    '''
    Debug Function to throw Errors 
    args:
        ~websocket
        path #path wich the websocket  
    return:
        None
    toDo:
        None
    '''
    name = ''
    connections.append(websocket)
    async for message in websocket:
        #does this coroutine every time a message arrives
        if(json.loads(message)['type'] == "disconnect"):
            connections.remove(websocket)
            await handler.miningPool.suspendedMiner(name)
            return
        result = await handler.main(message, websocket)
        try:
            name = result['name']
        except:
            pass
        if(result != {}):
            await websocket.send(json.dumps(result))
    connections.remove(websocket)
    await handler.miningPool.suspendedMiner(name)
    return
import config as cfg
if __name__ == "__main__":
    #port where miners register
    try:
        port = cfg.config['port']
        #set the executor to handle 
        start_server = websockets.serve(handleClient, cfg.config['serverAdress'] , cfg.config['port'])
        #start the server
        asyncio.get_event_loop().run_until_complete(start_server)
        print('\x1bc')
        
    except:
        print('Socketserver Starting Faild the port might be already in use')
        exit()
        pass
    try:
        print('Socketserver Initialised')
        asyncio.get_event_loop().run_forever()
    except:
        pass