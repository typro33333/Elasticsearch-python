from elasticsearch import Elasticsearch,RequestError,ElasticsearchException

class config:
    def __init__(self,host,scheme,port):
        self.host = host
        self.scheme = scheme
        self.port = port

##server = config('localhost',"http",9200) ##Local Host
server = config('tstsv.ddns.net',"http",9200)  ##Server

es = Elasticsearch(
    [server.host],
    scheme=server.scheme,
    port=server.port,
)