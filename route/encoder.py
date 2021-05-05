import numpy as np
import requests, faiss, os, json
from route.config import setting
import numpy as np

class UniversalEncoder():
        
    FEATURE_SIZE = 512
    BATCH_SIZE = 32
    vectors_dir = str(os.path.realpath("."))+"/search_data/faiss.index"
    data_dir = str(os.path.realpath("."))+"/search_data/faiss.txt"

    def __init__(self, host, port):
        self.server_url = "http://{host}:{port}/v1/models/model:predict".format(
            host = host,
            port = port
        )
        try:
            setting.index_on_ram = faiss.read_index(self.vectors_dir)
        except Exception:
            setting.index_on_ram = None
        try:
            setting.data_on_ram = json.load(open(self.data_dir,"r"))["data"]
        except Exception:
            setting.data_on_ram = []

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
        vector = self.encode(data)                                         #converter data to vectors
        if append == False:
            try:
                file = open(self.data_dir,"w")
            except Exception:
                os.mkdir(self.data_dir.split("/")[-2])
                file = open(self.data_dir,"w")
            file.write("")
            file.close()
            setting.index_on_ram = faiss.IndexFlatL2(self.FEATURE_SIZE)    #init the index
            setting.data_on_ram = []
        setting.index_on_ram.add(vector)
        setting.data_on_ram.extend(data)
        json.dump({"data":setting.data_on_ram},open(self.data_dir,"w"))
        faiss.write_index(setting.index_on_ram,self.vectors_dir)
        return setting.index_on_ram
    
    def search(self, query, numb_result:int=1):
        if setting.index_on_ram == None:
            setting.index_on_ram = faiss.read_index(self.vectors_dir)
        index = setting.index_on_ram
        query_vector = self.encode([query])
        top_k_result = index.search(query_vector, numb_result)
        print(len(setting.data_on_ram))
        return [
            setting.data_on_ram[_id] for _id in top_k_result[1].tolist()[0]
        ]
    
    def remove_index(self, query):
        try:
            #get current indexs
            if setting.index_on_ram == None:
                setting.index_on_ram = faiss.read_index(self.vectors_dir)
            #search index
            query_vector = self.encode([query])
            id = setting.index_on_ram.search(query_vector,1)[1][0][0]
            #remove data from index and data on ram
            setting.index_on_ram.remove_ids(np.array([id]))
            setting.data_on_ram.pop(id)
            #update data
            faiss.write_index(setting.index_on_ram,self.vectors_dir)
            file = open(self.data_dir,"w")
            file.write("")
            json.dump({"data":setting.data_on_ram},file)
            file.close()
        except Exception:
            return False
        return True

encoder = UniversalEncoder('localhost', '8501')