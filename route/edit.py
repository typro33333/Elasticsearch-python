from fastapi import APIRouter, Body, HTTPException,status,File, UploadFile
from typing import Optional
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
import numpy as np
import os,subprocess,time,re,requests
from func.call_index import call_all_index
from core.config_elastic import server,es
from faiss_pi4.test import encoder
route = APIRouter()

@route.get('/reset/faiss/{}')
def reset_faiss(comfirm:Optional[bool]=False):
    if comfirm == True:
        start = time.time()
        encoder.build_index(call_all_index(),False)
        stop = time.time()
        return [{'Status':'Build Complete'},{'time_lost':'{}s'.format(stop-start)}]
    else:
        raise HTTPException(status_code=404,detail='U must think again!')

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
    start = time.time()
    subprocess.run('curl -H "Content-Type: application/json" -XPOST "localhost:9200/{}/_bulk?pretty&refresh" --data-binary "@{}"'.format(indexname,filename),shell=True)
    encoder.build_index([indexname],True)
    stop = time.time()
    if keepfile is not True:
        os.remove(filename)
        return [{"index":indexname,"filename": file.filename},{'Status':'Complete Import data for elasticsearch!','Keep_file':False,'time_lost':stop-start}]
    else:
        return [{"index":indexname,"filename": file.filename},{'Status':'Complete Import data for elasticsearch!','Keep_file':True,'time_lost':stop-start}]

@route.post("/insert/indexname_v1")
async def insert_index_v1(indexname:Optional[str]=None):
    if indexname != None:
        indexname = indexname.lower()
        l = indexname.split(' ')
        abc =''
        for i in range(len(l)):
            if i == 0:
                abc = l[i]
            else:
                abc = abc+'-'+l[i]
        try:
            es.indices.create(index=abc)
            return {'Index':'{} create completed'.format(indexname)}
        except ElasticsearchException as error:
            raise HTTPException(status_code=402,detail=error.error)
    else:
        raise HTTPException(status_code=402,detail='Please fill index-name')

@route.post("/insert/indexname_v2")
async def insert_index_v2(indexname:Optional[str]=None):
    if indexname != None:
        indexname = re.sub(r"[^\w\s]",'',indexname.lower())
        indexname = re.sub(r"\s+", '-', indexname)
        try:
            start = time.time()
            es.indices.create(index=indexname)
            indexname = re.sub(r"[^\w\s]",' ',indexname.lower())
            encoder.build_index([indexname],True)
            stop = time.time()
            return {'Index':'{} create completed'.format(indexname),'time_spend':stop-start}
        except ElasticsearchException as error:
            raise HTTPException(status_code=402,detail=error.error)
    else:
        raise HTTPException(status_code=402,detail='Please fill index-name')

@route.post("/train/index_v1")
async def train_index_v1(index:list=Body(...,embed=True)):
    check = isinstance(index,list)
    if check == True:
        start = time.time()
        encoder.build_index(index,True)
        stop = time.time()
        raise HTTPException(status_code=200,detail={'Time_lost':stop-start})
    else:
        raise HTTPException(status_code=402,detail='wrong list input!')

@route.post("/delete/indexname")
async def delete_index(indexname:Optional[str]=None):
    if indexname == None:
        raise HTTPException(status_code=402,detail='field is empty cant not delete!')
    else:
        indexname = re.sub(r"[^\w\s]",'',indexname.lower())
        indexname = re.sub(r"\s+", '-', indexname)
        try:
            es.indices.delete(index=indexname)
            return {'delete_complete':''.format(indexname)}
        except ElasticsearchException as error:
            raise HTTPException(status_code=404,detail=error.error+' cant delete!')

@route.post("/delete_all/index")
async def delete_all_index(passwords:Optional[str]=None):
    if passwords == 'tt123':
        uri = "http://tstsv.ddns.net:9200/_cat/indices?format=json"
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
            try:
                start = time.time()
                for i in arr:
                    es.indices.delete(index=i)
                stop = time.time()
                raise HTTPException(status_code=200,detail=['Delete all index complete!',{'time_lost':'{}s'.format(stop-start)}])
            except ElasticsearchException as error:
                raise HTTPException(status_code=402,detail=error.error)
    else:
        raise HTTPException(status_code=404,detail='Error passwords')