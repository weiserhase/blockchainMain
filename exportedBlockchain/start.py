import subprocess
import json
import os
import sys
import config as cfg
ip = str(cfg.config['serverAdress'])+ ':' +str(cfg.config['port'])+'/'
#name = input('Namen Eingeben') #for external use
name = 'weiserhase'
executable = "python -m pip install websockets"
subprocess.Popen(['cmd.exe', executable], stdin=None, stdout=None, stderr=None)
executable = "python -m pip install asyncio"
subprocess.Popen(['cmd.exe', executable], stdin=None, stdout=None, stderr=None)
try:
    executable =str(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/") +"/miner.py"
    subprocess.Popen(['python', executable, ip, name], stdin=None, stdout=None, stderr=None)
    print('process started')
except KeyboardInterrupt:
    print('stopping Miner')
    exit()
    pass
