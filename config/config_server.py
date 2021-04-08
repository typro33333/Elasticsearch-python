class Config_Server:
    def __init__(self,HOST,PORT,RELOAD):
        self.HOST = HOST
        self.PORT = PORT
        self.RELOAD = RELOAD

Setting = Config_Server('localhost',8000,True)