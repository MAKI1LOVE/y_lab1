from fastapi import FastAPI

from src.api.v1 import v1_router
from src.database import init_db

app = FastAPI()

app.include_router(v1_router, prefix='/api/v1')


@app.on_event('startup')
async def startup():
    await init_db()


@app.on_event('shutdown')
async def shutdown():
    pass
