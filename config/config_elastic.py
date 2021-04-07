class config:
    def __init__(self,host,scheme,port):
        self.host = host
        self.scheme = scheme
        self.port = port

server = config('localhost',"http",9200)