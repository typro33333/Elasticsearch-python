from fastapi import APIRouter, Body, HTTPException,status,File, UploadFile
from typing import Optional
import numpy as np
from core.config_elastic import es
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
import re,time,requests
from func.call_index import call_all_index_v2
from route.encoder import encoder

route = APIRouter()

@route.get("/math_all/")
async def search_custom_indexname(indexname:str,page:Optional[int]=1):
    arr = []
    if indexname is not None:
        try:
            if indexname.find('-') == -1:
                indexname = indexname.lower()
                indexname = re.sub(r"\s+", '-', indexname)
            print(indexname)
            res = es.search(index=indexname, body={"query": {"match_all": {}}},from_=page)
            for hit in res['hits']['hits']:
                arr.append((hit['_source']))
            return arr
        except ElasticsearchException as err:
            raise HTTPException(status_code=402,detail=err.error)
    else:
        raise HTTPException(status_code=404,detail='index name is None')

@route.post('/the_similar_word')
async def search_similar(query:str=Body(...,embed=True),number:Optional[int]=Body(...,embed=True)):
    if query != None and number != None:
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%m/%d/%Y", named_tuple)
        start = time.time()
        a = encoder.search(query,number)
        data = []
        for i in a:
            data.append({'description':i})
        stop = time.time()
        return [data,{'time_lost':stop-start}]
    else:
        raise HTTPException(status_code=402,detail='search fill is none')

@route.post('/get_query/{name_index}')
async def search(name:str=Body(...,embed=True),id_index:str=Body(...,embed=True)):
    uri = "http://tstsv.ddns.net:9200/{}/_doc/{}".format(name,id_index)
    respose = requests.get(uri)
    if respose.status_code == 200:
        respose = respose.json()
        return respose['_source']
    else:
        raise HTTPException(status_code=401, detail="Error query")
        return

@route.post("/{}/query")
async def search_query(index:str,query:dict=Body(...,embed=True)):
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

