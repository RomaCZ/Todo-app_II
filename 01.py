from beanie_batteries_queue import Task, Runner

import asyncio


from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from backend.app.models.user import User
from backend.app.models.todo import Todo
from backend.app.api.v1.router import router



from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_dsn: str = "mongodb://localhost:27017/beanie_db"
    mongodb_db_name: str = "beanie_queue_db"

def settings():
    return Settings()

def cli(settings):
    client = AsyncIOMotorClient(settings.mongodb_dsn)
    client.get_io_loop = asyncio.get_running_loop
    return client

def db(cli=cli(settings()), settings=settings()):
    return cli[settings.mongodb_db_name]


class ExampleTask(Task):
    data: str

    async def run(self):
        self.data = self.data.upper()
        await self.save()
        #print("ddd")



async def app_init(db):
    models = [
        ExampleTask,
    ]
    await init_beanie(
        database=db,
        document_models=models,
    )

    yield None



if __name__ == '__main__':
    app_init(db)
    print("tu")

    from time import sleep
    #sleep(10)

    runner = Runner(task_classes=[ExampleTask])
    runner.start()