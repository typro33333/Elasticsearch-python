import numpy as np
import requests, torch, os
from faiss_pi4.config import setting
import numpy as np
from torch import nn
import os

class UniversalEncoder():
    FEATURE_SIZE = 512
    BATCH_SIZE = 32
    storage_dir = str(os.path.realpath("."))+"/search_data/faiss.index"

    def __init__(self, host, port):
        self.server_url = "http://{host}:{port}/v1/models/model:predict".format(
            host = host,
            port = port
        )

    @staticmethod
    def _standardized_input(sentence:str):
        return sentence.replace("\n", "").lower().strip()[:1000]

    def encode(self,data):
        data = [self._standardized_input(sentence=sentence) for sentence in data]
        all_vectors = []
        for i in range(0, len(data), self.BATCH_SIZE):
            batch = data[i:i+self.BATCH_SIZE]
            res = requests.post(
                url=self.server_url,
                json = {"instances":batch}
            )
            if not res.ok:
                print("FALSE")
            all_vectors += torch.transpose(torch.Tensor([list(res.json()["predictions"])]),0,1)
        return all_vectors

    def build_index(self, data:list, append:bool=True):
        if append == True:
            setting.index_on_ram = torch.load(self.storage_dir)
        setting.index_on_ram.extend(self.encode(data))                      #converter data to vectors
        try:
            torch.save(setting.index_on_ram,self.storage_dir)
        except:
                os.mkdir(self.storage_dir.split("/")[-2])
                torch.save(setting.index_on_ram,self.storage_dir)
        return setting.index_on_ram
    
    def search(self,data, query, numb_result:int=1):
        query_vector = self.encode([query])[0]                              #converter data to vectors
        cos = nn.CosineSimilarity(dim=1, eps=1e-6)                          #init comparse functions

        if setting.index_on_ram == []:                                      
            setting.index_on_ram = torch.load(self.storage_dir)
        temp_vectors = setting.index_on_ram.copy()
        distances = []                                                      #comparse distances
        for i in range(len(temp_vectors)):
            distances.append(float(cos(temp_vectors[i], query_vector)))
        index_results = []                                                  #get the top n index has closest semantics
        min_distance = min(distances)
        for i in range(numb_result):
            index = distances.index(max(distances))
            index_results.append(index)
            distances[index] = min_distance
        result = []                                                         #get top n result
        for i in index_results:
            result.append(data[i])
        return result
    
    def remove_index(self, query):
        query_vector = self.encode([query])[0]                              #converter data to vectors
        cos = nn.CosineSimilarity(dim=1, eps=1e-6)                          #init comparse functions

        if setting.index_on_ram == []:                                      
            setting.index_on_ram = torch.load(self.storage_dir)
        temp_vectors = setting.index_on_ram.copy()
        distances = []                                                      #comparse distances
        for i in range(len(temp_vectors)):
            distances.append(float(cos(temp_vectors[i], query_vector)))
        index = distances.index(max(distances))                             #get the delete index
        setting.index_on_ram.pop(index)
        torch.save(setting.index_on_ram,self.storage_dir)
        return setting.index_on_ram