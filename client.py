import asyncio
import websockets
import json
import matplotlib.pyplot as plt
import string 
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
async def chain():
    uri = "ws://185.245.96.117:8765"
    async with websockets.connect(uri) as websocket:
        #name = input("Function?: ")
        name = {'type':'getChain'}
        await websocket.send(json.dumps(name))

        greeting = await websocket.recv()
        print(greeting)

async def hello():
    uri = "ws://185.245.96.117:8765"
    async with websockets.connect(uri) as websocket:
        print(websocket)
        #name = input("Function?: ")
        data = []
        for i in range(20000):
            data.append({'name': id_generator(6), 'fee': random.random()})
        msg = {'type':'newTransaction','data':data}
        await websocket.send(json.dumps(msg))

        await websocket.send(json.dumps({'type':'disconnect'}))

        greeting = await websocket.recv()
        print(greeting)

async def graph():
    uri = "ws://185.245.96.117:8765"
    async with websockets.connect(uri) as websocket:
        print(websocket)
        #name = input("Function?: ")
        
        #for i in range(20):
        name = {'type':'getTimings'}
        await websocket.send(json.dumps(name))

        await websocket.send(json.dumps({'type':'disconnect'}))

        greeting = json.loads(await websocket.recv())
        #plt.plot(greeting)
        #plt.show()

        print(greeting)
i = input('getChain/newTransaction')

if(i == '0'):
    asyncio.get_event_loop().run_until_complete(chain())
elif(i == '1'):
    asyncio.get_event_loop().run_until_complete(hello())
elif(i == '2'):
    asyncio.get_event_loop().run_until_complete(graph())
else:
    print('not a function')
