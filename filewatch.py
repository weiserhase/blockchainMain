import sys
import logging
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import subprocess
import signal
import time
def restartWebsocket():
    print('Datei wurde Geändert')
    '''
    executable = "c:/Users/Jan/Documents/GitHub/python_test/blockchain/pool/miningPool.py "
    process = subprocess.Popen(['python.exe', executable], stdin=None, stdout=None, stderr=None)
    pid = process.pid
    #print(process.pid)
    return[process, pid]
    '''
    return[0,0]
class Event(LoggingEventHandler):
    def __init__(self):

        new = restartWebsocket()
        self.process = new[0]
        self.pid = new[1]

        
    def dispatch(self, event):
        #os.kill(self.pid, signal.SIGTERM)
        new = restartWebsocket()
        self.process = new[0]
        self.pid = new[1]
        

    pass
if __name__ == "__main__":
    
    event_handler = Event()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = '.' 
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
            #observer.join(1)
    except (KeyboardInterrupt, SystemExit):
        os.kill(event_handler.pid, signal.SIGTERM)
        observer.stop()
    observer.join()
