class Config_Server:
    def __init__(self,HOST,PORT,RELOAD):
        self.HOST = HOST
        self.PORT = PORT
        self.RELOAD = RELOAD

##Setting = Config_Server('localhost',8000,True) ##Localhost
Setting = Config_Server('0.0.0.0',8000,True) ##Server