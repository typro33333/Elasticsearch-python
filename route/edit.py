from fastapi import APIRouter, Body, HTTPException,status,File, UploadFile
from typing import Optional
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
import requests
import numpy as np
import os
import subprocess
from faiss_func.call_index import encoder
route = APIRouter()

@route.post("/uploadfile/new_index")
async def create_upload_file(
indexname:str=Body(...,embed=True),
file: UploadFile = File(...),
keepfile:Optional[str]=False):
    path = '/Users/thinh/Desktop/elasticsearch/api'
    random = np.random.choice(20)
    f = open('{}_'.format(random)+file.filename,'wb')
    f.write(file.file.read())
    filename = '{}_'.format(random)+file.filename
    x = os.path.join(path,'{}_'.format(random)+file.filename)
    subprocess.run('curl -H "Content-Type: application/json" -XPOST "localhost:9200/{}/_bulk?pretty&refresh" --data-binary "@{}"'.format(indexname,filename),shell=True)
    encoder.build_index([indexname])
    if keepfile is not True:
        os.remove(filename)
        return [{"index":indexname,"filename": file.filename},{'Status':'Complete Import data for elasticsearch!','Keep_file':False}]
    else:
        return [{"index":indexname,"filename": file.filename},{'Status':'Complete Import data for elasticsearch!','Keep_file':True}]

@route.post("/delete/indexname")
async def delete_index(indexname:Optional[str]=None):
    if indexname == None:
        raise HTTPException(status_code=402,detail='field is empty cant not delete!')
        return
    else:
        try:
            es.indices.delete(index=indexname)
        except ElasticsearchException as error:
            raise HTTPException(status_code=404,detail=error.error+' cant delete!')