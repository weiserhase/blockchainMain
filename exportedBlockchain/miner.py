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
import config as cfg
import platform

from hashrate import hahrate
class Handler:
    ''' 
    This class handels socketServer requests and call the functions by the type submited in message

    #Documentation
    self is not considered as argument because it is automaticly updated and the values are initalised in __init__
    Objects are marked with ~ infront of them 
    '''
    def __init__(self):
        self.last = 0
        self.process = ''
        self.term = False
        self.change = []
    async def proc(self):
        out = self.process.stdout.read()
        if(platform.system() == 'Windows'):
            os.kill(self.last, signal.CTRL_C_EVENT)
        else:
            os.kill(self.last, signal.SIGKILL)

    async def main(self, message, websocket):
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
        if(message['type'] == 'getData'):
            websocket.send(json.dumps(self.change))

        if(message['type'] == 'newJob'):
            if(self.last != 0):
                try:
                    if(self.process.returncode != None):
                        self.process.terminate()
                except:
                    pass
            executable =str(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/") +"/mine.py"
            try:
                cfg.config['hash'] = message['data'][5]
                self.change = [json.dumps(message['data'][0]), json.dumps(message['data'][1])]
                args = ['python', executable, "ws://"+str(sys.argv[1]),'', json.dumps(message['data'][2]),  json.dumps(message['data'][3]), json.dumps(message['data'][4]), sys.argv[1],sys.argv[2]]
                    
                print('starting new Job with Difficulty: ' +str(message['data'][4]) )
                self.process = subprocess.Popen(args , stdin=None, stdout=None, stderr=None)
            except Exception as e:
                print('Failed to start Subprocess with Eception:' +str(e) )
                pass
            pid = self.process.pid
            self.last = pid
        
        if(message['type'] == 'share'):
            if(message['data']['status'] == 'Declined'):
                if(self.term == True):
                    self.term = True
                    self.process.terminate()
            else:
                #print('Share '+str(message['data']['status'])+' by Pool! You submitted '+ str(message['data']['accepted'])+ ' accepted shares; '+ str(message['data']['rejected']) +' rejected;', end='\n')
                pass
            pass


handler = Handler()

async def handleMessages():
    '''
    this Function is used to handle new Incoming Messages
    args:
        ~websocket
        path #path wich the websocket  
    return:
        ~any  #no json.dumps but no class result 
    toDo:
        None
    '''
    uri = "ws://"+str(sys.argv[1])
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({'type': 'registerMiner', 'data':{'name':sys.argv[2], 'hashrate':hashrate}}))
            print('registered on Pool with username: ' +name + 'with a hashrate of: ' +str(hashrate/1e6) +' MHash/s')
            async for message in websocket:
                try:
                    if(message == 'null'):
                        pass
                    
                    if(json.loads(message)['type'] == 'newJob'):
                        await  (handler.main(message, websocket))
                    
                    if(json.loads(message)['type'] == 'exit'):
                        continue
                    
                    if(json.loads(message)['type'] == 'share'):
                        await  (handler.main(message, websocket))
                        continue
                except:
                    pass
    except:
        pass


if __name__ == "__main__":
    #mainloop for starting the recv
    ip = sys.argv[0]
    name = sys.argv[1]
    size = int(multiprocessing.cpu_count())
    data = []
    for i in range(multiprocessing.cpu_count()):
        data.append(size)
    start = time.time()
    print((time.time()-start))
    #hashrate = (1/(time.time()-start))
    hashrate = hahrate()
    print('mining with: '+str(hashrate))
    multiprocessing.freeze_support()
    try:
        asyncio.get_event_loop().run_until_complete(handleMessages())
    except KeyboardInterrupt:
        print('stopping Miner')
        exit()
        pass