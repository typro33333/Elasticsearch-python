import requests
from faiss_func.encoder import UniversalEncoder

##encoder = UniversalEncoder("tstsv.ddns.net", 8501)
encoder = UniversalEncoder("tstsv.ddns.net", 8501)

def call_all_index():
    uri = "http://localhost:9200/_cat/indices?format=json"
    response = requests.get(uri)
    arr = []
    if response.status_code == 200:
        response = response.json()
        for i in range(len(response)):
            if response[i]['index'].startswith('.',0,1) == True:
                continue
            arr.append(response[i]['index'])
        return arr

def check_compase(query:str):
    encoder.build_index(call_all_index(),False)
    return encoder.search(call_all_index(),query,2)
    