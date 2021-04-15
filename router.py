from fastapi import APIRouter
from route import info,search,edit

api_router = APIRouter()

api_router.include_router(info.route, prefix='/info', tags=['info-elastic'])
api_router.include_router(edit.route,prefix='/edit',tags=['edit-elastic'])
api_router.include_router(search.route,prefix='/search', tags=['search-elastic'])