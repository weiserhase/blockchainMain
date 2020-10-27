
from hashlib import sha512, sha256
print(len(sha512('test'.encode()).hexdigest()))
print(len(sha256('test'.encode()).hexdigest()))