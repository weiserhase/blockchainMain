import multiprocessing
import string 
import random
from hashlib import sha512, blake2b, blake2s
import json
import time
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def has(ar):
    res = []
    for element in range(int(1e6)//multiprocessing.cpu_count()):
        res.append(blake2s(json.dumps(id_generator(10)).encode()).hexdigest())
    return res
def col(i):
    col = []
    for i in range(int(1e6)):
        col.append(id_generator())
    return col

def hahrate():
    count = multiprocessing.cpu_count()
    with multiprocessing.Pool(count) as p:
        inp = p.map(has, range(count))
        start = time.time()
        result = p.map(has, inp)
    td = (time.time() - start)
    print(td)
    return (1e6/td)
if __name__ == "__main__":
    multiprocessing.freeze_support()
    print(hahrate())