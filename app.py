from fastapi import FastAPI,Body,status,HTTPException,File, UploadFile
import requests
import json
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
from config.config_elastic import server
from config.config_server import Setting
import os
from io import BytesIO
import tempfile
import numpy as np
import subprocess
import sys
from typing import Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

f = tempfile.SpooledTemporaryFile()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch(
    [server.host],
    scheme=server.scheme,
    port=server.port,
)

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
            if repose[i]['index'].startswith('.',0,1) == True:
                continue
            arr.append(repose[i]['index'])
        if len(arr) == 0:
            raise HTTPException(status_code=404,detail='Data doesnt have index!')
            return
        return arr
    else:
        raise HTTPException(status_code=404,detail="Server Down")
        return

@app.get("/index/total_value_index")
async def total_value_index(index:Optional[str]=None):
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
async def create_upload_file(
indexname:str=Body(...,embed=True),
file: UploadFile = File(...),
keepfile:Optional[str]=True):
    path = '/Users/thinh/Desktop/elasticsearch/api'
    random = np.random.choice(20)
    f = open('{}_'.format(random)+file.filename,'wb')
    f.write(file.file.read())
    filename = '{}_'.format(random)+file.filename
    x = os.path.join(path,'{}_'.format(random)+file.filename)
    subprocess.run('curl -H "Content-Type: application/json" -XPOST "localhost:9200/{}/_bulk?pretty&refresh" --data-binary "@{}"'.format(indexname,filename),shell=True)
    if keepfile is not True:
        os.remove(filename)
        return [{"index":indexname,"filename": file.filename},{'Status':'Complete Import data for elasticsearch!','Keep_file':False}]
    else:
        return [{"index":indexname,"filename": file.filename},{'Status':'Complete Import data for elasticsearch!','Keep_file':True}]

@app.post("/delete/indexname")
async def delete_index(indexname:Optional[str]=None):
    if indexname == None:
        raise HTTPException(status_code=402,detail='field is empty cant not delete!')
        return
    else:
        try:
            es.indices.delete(index=indexname)
        except ElasticsearchException as error:
            raise HTTPException(status_code=404,detail=error.error+' cant delete!')



if __name__ == '__main__':
    subprocess.run('pip install -r requirements.txt')
    uvicorn.run('test:app', host = Setting.HOST, port = Setting.PORT, reload = Setting.RELOAD)