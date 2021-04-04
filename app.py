from fastapi import FastAPI,Body,status,HTTPException
import requests
app = FastAPI()
import json
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ['localhost'],
    scheme="http",
    port=9200,
)

search_param = {
    'query': {
        'match': {
            'field1': 'find me!'
        }
    }
}
some_string = '{"name" : "student"}'
some_dict = json.loads(some_string)

@app.get("/health")
async def get_heal():
    r = requests.get('http://localhost:9200/_cat/health?format=json')
    response = r.json()
    if response.status_code == 200:
        return response
    else:
        raise HTTPException(status_code=401,detail='Server error')
        return

@app.post('/get_query/{name_index}')
async def search(name:str=Body(...,embed=True),id_index:str=Body(...,embed=True)):
    uri = "http://localhost:9200/{}/_doc/{}".format(name,id_index)
    respose = requests.get(uri)
    if respose.status_code == 200:
        respose = respose.json()
        return respose['_source']
    else:
        raise HTTPException(status_code=401, detail="Error query")
        return
    
@app.get('/get_all_index')
async def get_all_index():
    uri = "http://localhost:9200/_cat/indices?format=json"
    repose = requests.get(uri)
    arr = []
    if repose.status_code == 200:
        repose = repose.json()
        for i in range(len(repose)):
            arr.append(repose[i]['index'])
        return arr
    else:
        raise HTTPException(status_code=404,detail="Server Down")
        return

@app.post("/search/")
async def search_query(index:str=Body(...,embed=True)):
    req = es.get(index='bank',id=1)
    print(req)
