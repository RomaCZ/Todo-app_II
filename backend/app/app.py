from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.core.config import settings
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from backend.app.models.user import User
from backend.app.models.todo import Todo
from backend.app.models.vvz import SearchResult
from backend.app.api.v1.router import router



@asynccontextmanager
async def app_init(app: FastAPI):
    """ Initialize crucial application services """
    
    db_client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING, uuidRepresentation="standard")
    await init_beanie(
        database=db_client.todolist,
        document_models=[
            User,
            Todo,
            SearchResult,
            ]
    )
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=app_init
)

app.include_router(router, prefix=settings.API_V1_STR)
