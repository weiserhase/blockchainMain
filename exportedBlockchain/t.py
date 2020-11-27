'''
from hashlib import sha512, sha256
import platform
import threading
import time
import concurrent.futures
def wait():
    time.sleep(1)
    return(sha256('t'.encode()).hexdigest())
th = []
start = time.time()
with concurrent.futures.ThreadPoolExecutor() as executor:
    future = executor.submit(wait)
    print('test')
    return_value = future.result()
    print(return_value)
print(time.time()-start)
'''
print('test')