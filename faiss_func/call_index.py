import requests
from faiss_func.encoder import UniversalEncoder
from core.config_elastic import es
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

def total_index():
    final_indices = es.indices.get_alias().keys()
    return {'total':len(final_indices)-2}

def check_compase(query:str):
    return encoder.search(call_all_index(),query,2)
    