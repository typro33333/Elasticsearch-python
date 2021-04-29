from elasticsearch import Elasticsearch,RequestError,ElasticsearchException

class config:
    def __init__(self,host,protocol,port):
        self.host = host
        self.protocol = protocol
        self.port = port

server = config('localhost',"http",9200) ##Local Host
##server = config('tstsv.ddns.net',"http",9200)  ##Server

es = Elasticsearch(
    [server.host],
    http=server.protocol,
    port=server.port,
    timeout=1000000,
)