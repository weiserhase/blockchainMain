import asyncio
import websockets
import _thread
import json
import signal
import os
import subprocess
import multiprocessing
import hashlib
import random
import string
import time
import numpy as np
import sys
from multiprocessing import Pool

class Handler:
    def __init__(self):
        self.last = 0
        self.process = ''
    def main(self, message):
        message = json.loads(message)
        if(message['type'] == 'newJob'):
            print('New Job accepted')
            if(self.last != 0):
                try:
                    os.kill(self.last, signal.CTRL_C_EVENT)
                except :
                    pass
            #print('newJob')
            executable = "c:/Users/Jan/Documents/GitHub/python_test/blockchain/exportedBlockchain/mine.py"
            #print(message['data'])
            try:
                self.process = subprocess.Popen(['python', executable, json.dumps(message['data'][0]),json.dumps(message['data'][1]), json.dumps(message['data'][2]),  json.dumps(message['data'][3]), json.dumps(message['data'][4]), sys.argv[1],sys.argv[2]], stdin=None, stdout=None, stderr=None)           
            except :
                pass
            pid = self.process.pid
            self.last = pid
        
        if(message['type'] == 'share'):
            print('Share '+str(message['data']['status'])+' by Pool! You submitted '+ str(message['data']['accepted'])+ ' accepted shares; '+ str(message['data']['rejected']) +' rejected;')
            pass


handler = Handler()
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def has(x):
    res = []
    for i in range(x):
        res.append(hashlib.sha256(id_generator(10).encode('utf-8')))

async def recv():
    uri = "ws://"+str(sys.argv[1])
    print(uri)

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({'type': 'registerMiner', 'data':{'name':sys.argv[2], 'hashrate':hashrate}}))
        print('registered on Pool with username: ' +name + 'with a hashrate of: ' +str(hashrate) +' MHash/s')
        async for message in websocket:
            try:
                if(message == 'null'):
                    pass
                if(json.loads(message)['type'] == 'newJob'):
                    handler.main(message)
                
                if(json.loads(message)['type'] == 'exit'):
                    continue
                
                if(json.loads(message)['type'] == 'share'):
                    handler.main(message)
                    continue
            except:
                pass


if __name__ == "__main__":
    ip = sys.argv[0]
    name = sys.argv[1]
    #print(sys.argv)
    size = int(1e6/multiprocessing.cpu_count())
    data = []
    for i in range(multiprocessing.cpu_count()):
        data.append(size)
    start = time.time()
        #p.map(has, data)
    print((time.time()-start))
    #hashrate = (1/(time.time()-start))
    hashrate = 100
    print('mining with:'+str(hashrate))
    multiprocessing.freeze_support()
    try:
        asyncio.get_event_loop().run_until_complete(recv())
    except KeyboardInterrupt:
        pass