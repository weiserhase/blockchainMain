config ={
    'port': 8765, #the port #possible *int /standard is 8765
    'serverAdress': '185.245.96.117',
    'initDifficulty': 5, #the start difficulty #possible *int /standard is 5 
    'hash': 'sha512', #wich hash function should be used #possible sha256, sha512, blake2s /standard is sha512 //further will follow 
    'lastHashes': 50, #gives how many hashrates are considered in actual hashrate # possible *int /standard is 50 // 
    'blockSize': 200, #the amount of transactions in one job in bytes standart is 200 b
    'blockSizeUnit': 'b', #unit of blocksize
    #Database Config
    'dbHost': 'localhost',
    'dbUser': 'root',
    'dbPassword': 'mpgsas2020',
    'dbDatabaseName': 'blockchain'
}