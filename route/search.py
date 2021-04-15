from fastapi import APIRouter, Body, HTTPException,status,File, UploadFile
from typing import Optional
import requests
import numpy as np
from core.config_elastic import es
from elasticsearch import Elasticsearch,RequestError,ElasticsearchException
from faiss_func.call_index import check_compase
route = APIRouter()

@route.post('/the_similar_word/{}')
async def search_similar(query:Optional[str]=None):
    return check_compase(query)

@route.post('/get_query/{name_index}')
async def search(name:str=Body(...,embed=True),id_index:str=Body(...,embed=True)):
    uri = "http://localhost:9200/{}/_doc/{}".format(name,id_index)
    respose = requests.get(uri)
    if respose.status_code == 200:
        respose = respose.json()
        return respose['_source']
    else:
        raise HTTPException(status_code=401, detail="Error query")
        return

@route.post("/index/query")
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

@route.post("/custom/indexname")
async def search_custom_indexname(indexname:Optional[str]=None):
    return 'this api not complete!'

