from fastapi import APIRouter, Body, HTTPException
from typing import Optional
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
from core.config_elastic import es
route = APIRouter()
import requests
from func.call_index import total_index
import re

@route.get("/health")
async def get_heal():
    r = requests.get('http://tstsv.ddns.net:9200/_cat/health?format=json')
    if r.status_code == 200:
        response = r.json()
        return response
    else:
        raise HTTPException(status_code=401,detail='Server error')
        return
    
@route.get('/get_all_index_v1')
async def get_all_index_v1():
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
            return
        return arr
    else:
        raise HTTPException(status_code=404,detail="Server Down")
        return

@route.get('/get_all_index_v2')
async def get_all_index_v2():
    response = es.indices.get('*')
    l_index = []
    for key in [*response]:
        l_index.append(re.sub(r"[^\w\s]", ' ', key))
    return [{'total_index':len(l_index)},l_index]

@route.get('/total_index')
async def total():
    return total_index()