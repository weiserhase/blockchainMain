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
from multiprocessing import Pool

class Handler:
    def __init__(self):
        self.last = 0
        self.process = ''
    def main(self, message):
        message = json.loads(message)
        if(message['type'] == 'newJob'):
            if(self.last != 0):
                os.kill(self.last, signal.CTRL_C_EVENT)
            #print('newJob')
            executable = "c:/Users/Jan/Documents/GitHub/python_test/blockchain/miner/mine.py"
            #print(message['data'])

            self.process = subprocess.Popen(['python', executable, json.dumps(message['data'][0]),json.dumps(message['data'][1]), json.dumps(message['data'][2]),  json.dumps(message['data'][3]), json.dumps(message['data'][4])], stdin=None, stdout=None, stderr=None)           
            print('process started')
            pid = self.process.pid
            self.last = pid


handler = Handler()
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def has(x):
    res = []
    for i in range(x):
        res.append(hashlib.sha256(id_generator(10).encode('utf-8')))

async def recv():
    uri = "ws://185.245.96.117:8765"
    async with websockets.connect(uri) as websocket:
        name = "weiserhase"
        await websocket.send(json.dumps({'type': 'registerMiner', 'data':{'name':name, 'hashrate':hashrate}}))
        print('registered on Pool with username: ' +name + 'with a hashrate of: ' +str(hashrate) +' MHash/s')
        async for message in websocket:
            #print(message)
            if(json.loads(message)['type'] == 'newJob'):
                handler.main(message)
            
            if(json.loads(message)['type'] == 'exit'):
                continue


if __name__ == "__main__":
    size = int(1e6/multiprocessing.cpu_count())
    data = []
    for i in range(multiprocessing.cpu_count()):
        data.append(size)
    start = time.time()
    with Pool(16) as p:
        p.map(has, data)
    print((time.time()-start))
    hashrate = (1/(time.time()-start))
    print('mining with:'+str(hashrate))
    multiprocessing.freeze_support()
    asyncio.get_event_loop().run_until_complete(recv())