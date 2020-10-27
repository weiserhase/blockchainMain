import asyncio
import websockets
import json
async def chain():
    uri = "ws://185.245.96.117:8765"
    async with websockets.connect(uri) as websocket:
        #name = input("Function?: ")
        name = {'type':'getChain' }
        
        await websocket.send(json.dumps(name))

        greeting = await websocket.recv()
        print(greeting)

async def hello():
    uri = "ws://185.245.96.117:8765"
    async with websockets.connect(uri) as websocket:
        print(websocket)
        #name = input("Function?: ")
        name = {'type':'newTransaction','data':{'name': 'Jan KEller'}}

        await websocket.send(json.dumps(name))

        await websocket.send(json.dumps({'type':'disconnect'}))

        greeting = await websocket.recv()
        print(greeting)
i = input('getChain/newTransaction')

if(i == '0'):
    asyncio.get_event_loop().run_until_complete(chain())
else:
    asyncio.get_event_loop().run_until_complete(hello())
