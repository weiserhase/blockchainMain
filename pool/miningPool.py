import json
import blockchain
import subprocess
import externalBlockchain
import asyncio
class MiningPool:
    def __init__(self):
        self.openTransactions = []
        self.openJobs = []
        self.miners = {}
        self.jobsize = 100
        self.blockchain = externalBlockchain.blockchain
        executable = "/python/blockChain/miner/miner.py"
        self.process = subprocess.Popen(['python', executable], stdin=None, stdout=None, stderr=None)
        print('miner started')
    def getJob(self):
        if(len(self.openJobs) > 0):
            job = self.openJobs[0]
            self.openJobs.remove(0)
            return job
        else:
            generated = self.generateNewJob()
            if(generated  == False):
                return False
            
            job = self.openJobs[0]
            self.openJobs.remove(0)
            return job
    async def generateNewJob(self):
        self.openJobs = []
        if(len(self.openTransactions) == 0):
            return False
        ma = 2**64
        perMiner = ma/len(self.miners)
        data = []
        for i in range(len(self.miners)):
            start = i*perMiner
            data.append([self.openTransactions[0], (externalBlockchain.getChain()), start,  start+ perMiner])
        self.openJobs = data 
        
        del self.openTransactions[0]
        for index in range(len(self.openJobs)):
            await( list(self.miners.values())[index][0].send(json.dumps({'type':'newJob', 'data' :data[index]})))


        
    async def registerMiner(self, args, websocket):
        #args[0] = websocket
        #args[1] = name
        #stat array = [shares, , rejected , hashrate, ]
        self.miners[args['name']] = ([websocket, [0,0,0]])
        print(len(self.miners))
        if(self.openJobs == []):
            return {'type': 'exit'}
        else:
            await websocket.send(json.dumps(self.openJobs[0]))
    async def submitShare(self, args):
        print('submit')
        #args[0] name
        #args[1] data[block, proof, hashrate]
        #------------#
        #check if proof and nonce are valid
        block = (args[1][0])
        bl = externalBlockchain.Block(block['index'], block['transactions'], block['timestamp'], block['previous_hash'], block['nonce'])
        Block = bl
        print(externalBlockchain.is_valid_proof(Block, args[1][1]))
        if(externalBlockchain.is_valid_proof(Block, args[1][1])):
            print('Accepted')
            self.miners[args[0]][1][0]  += 1
            self.miners[args[0]][1][1]  = args[1][1]
            externalBlockchain.add_block(Block, args[1][1])
            await self.generateNewJob()
            #print(self)
            return 'Accepted'
        else:
            print('Declined')
            self.miners[args[0]][1][1]  += 1
            self.miners[args[0]][1][1]  = args[1][1]
            return 'Rejectd'
    async def newTransaction(self, args):
        #args = data
        self.openTransactions.append(args)
        if(self.openJobs == []):
            await self.generateNewJob()
        return externalBlockchain.getChain()
    
    async def getChain(self):
        return externalBlockchain.getChain()

        

class Handler:
    def __init__(self):
        self.miningPool = MiningPool()
    async def main(self , message, websocket):
        message = json.loads(message)
        
        if(message['type'] == "getChain"):
            result = await self.miningPool.getChain()
            return result
        
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

import websockets
import asyncio 

connections = list()
handler = Handler()
async def echo(websocket, path):
    print(websocket)
    connections.append(websocket)
    async for message in websocket:
        print(connections)
        
        if(json.loads(message)['type'] == "disconnect"):
            connections.remove(websocket)
            return
        result = await handler.main(message, websocket)
        await websocket.send(json.dumps(result))
if __name__ == "__main__":
    #port where miners register
    port = 8765
    start_server = websockets.serve(echo, "185.245.96.117", port)
    try:
        asyncio.get_event_loop().run_until_complete(start_server)
    except:
        pass
    print('Socketserver Initialised')
    asyncio.get_event_loop().run_forever()



