import numpy as np
import requests, faiss, os
from config import setting
import numpy as np

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
            all_vectors += res.json()["predictions"]
        all_vectors = np.array(all_vectors,dtype="f")
        return all_vectors
    
    def build_index(self, data:list, append:bool=True):
        vector = self.encode(data)                      #converter data to vectors
        index = faiss.IndexFlatL2(self.FEATURE_SIZE)
        if append == True:
            index = faiss.read_index(self.storage_dir)
        index.add(vector)
        faiss.write_index(index,self.storage_dir)
        setting.index_on_ram = index
        return index
    
    def search(self, data, query, numb_result:int=1):
        if setting.index_on_ram == None:
            setting.index_on_ram = faiss.read_index(self.storage_dir)
        index = setting.index_on_ram
        query_vector = self.encode([query])
        top_k_result = index.search(query_vector, numb_result)
        return [
            data[_id] for _id in top_k_result[1].tolist()[0]
        ]
    def remove_index(self, query):
        #get current indexs
        if setting.index_on_ram == None:
            setting.index_on_ram = faiss.read_index(self.storage_dir)
        index = setting.index_on_ram
        #search index
        query_vector = self.encode([query])
        id = index.search(query_vector,1)[1][0][0]
        #remove data from index
        index.remove_ids(np.array([id]))
        #update data
        faiss.write_index(index,self.storage_dir)
        setting.index_on_ram = index
        return index

encoder = UniversalEncoder("tstsv.ddns.net", 8501)