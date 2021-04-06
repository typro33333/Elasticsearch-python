from fastapi import FastAPI,Body,status,HTTPException,File, UploadFile
import requests
app = FastAPI()
import json
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
from config import server
import os
from io import BytesIO
import tempfile
import numpy as np

f = tempfile.SpooledTemporaryFile()

es = Elasticsearch(
    [server.host],
    scheme=server.scheme,
    port=server.port,
)

some_string = '{"name" : "student"}'
some_dict = json.loads(some_string)

@app.get("/health")
async def get_heal():
    r = requests.get('http://localhost:9200/_cat/health?format=json')
    if r.status_code == 200:
        response = r.json()
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

@app.post("/index/total_value_index")
async def total_query(index:str=Body(...,embed=True)):
    try:
        result = es.search(index='{}'.format(index),body={"query":{"match_all":{}}})
        arr = []
        arr.append({'total':result['hits']['total']['value']})
        return arr
    except ElasticsearchException as err:
        attributes = [attr for attr in dir(err) if not attr.startswith('__')]
        raise HTTPException(status_code=402,detail=err.error)
        return

@app.post("/index/search/query")
async def search_query(index:str=Body(...,embed=True),query:dict=Body(...,embed=True)):
    query_body = {
        "query": {
            "bool":{
                "must":{
                    "match": query
                }
            }
        }
    }
    try:
        result = es.search(index='{}'.format(index),body=query_body)
        return result
    except ElasticsearchException as err:
        raise HTTPException(status_code=402,detail=err.error)
        return 

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    path = '/Users/thinh/Desktop/elasticsearch'
    random = np.random.choice(20)
    f = open('{}_'.format(random)+file.filename,'wb')
    f.write(file.file.read())
    x = os.path.join(path,'{}_'.format(random)+file.filename)
    print(x)
    return {"filename": file.filename}
