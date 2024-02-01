import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from beanie_batteries_queue import Task, Runner, Priority



class ExampleTask(Task):
    data: str

    async def run(self):
        self.data = self.data.upper()
        await self.save()
        


# This is an asynchronous example, so we will access it from an async function
async def example():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.db_name, 
                    document_models=[ExampleTask]
                    )

    # Producer
    task = ExampleTask(data="test", priority=Priority.HIGH)
    await task.push()

    # Consumer
    runner = Runner(task_classes=[ExampleTask])
    runner.start()

    # Results in error:
    # File "C:\Git\Todo-app_II\.venv\Lib\site-packages\beanie\odm\documents.py", line 1024, in get_settings
    # raise CollectionWasNotInitialized
    # beanie.exceptions.CollectionWasNotInitialized


if __name__ == "__main__":
    asyncio.run(example())
