#!/usr/bin/python
import asyncio
import websockets
import extermalBlockchain
import json
import os 
import sys
import subprocess
import setproctitle
#setproctitle.setproctitle('test')
#start all scrpits
class requesthandler: 
    def main(message):
        if(message == "newTransaction"):
            result = extermalBlockchain.newTransaction()
            return result
        if( message == "getChain"):
            result = extermalBlockchain.getChain()
            return result
if __name__ == "__main__":
    async def echo(websocket, path):
        async for message in websocket:
            result = requesthandler.main(message)
            await websocket.send(json.dumps(result))
    start_server = websockets.serve(echo, "localhost", 8765)
    try:
        asyncio.get_event_loop().run_until_complete(start_server)
    except:
        pass
    print('Socketserver Initialised')
    asyncio.get_event_loop().run_forever()

