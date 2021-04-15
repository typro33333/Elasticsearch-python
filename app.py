from fastapi import FastAPI
from core.config_server import Setting
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from router import api_router
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Router
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run('app:app', host = Setting.HOST, port = Setting.PORT, reload = Setting.RELOAD)