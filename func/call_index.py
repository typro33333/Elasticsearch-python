import requests
from core.config_elastic import es
import re

def call_all_index_v1():
    response = es.indices.get('*')
    return [*response]

def call_all_index_v2():
    response = es.indices.get('*')
    l_index = []
    for key in [*response]:
        l_index.append(re.sub(r"[^\w\s]", ' ', key))
    return l_index

def total_index():
    final_indices = es.indices.get_alias().keys()
    return {'total':len(final_indices)-2}

    