import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from beanie_batteries_queue import Task, Runner, Priority, Queue


class ExampleTask(Task):
    data: str

    async def run(self):
        self.data = self.data.upper()
        await self.save()
        


async def initialize_beanie():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.db_name, 
                    document_models=[ExampleTask])


async def main():
    await initialize_beanie()
    
    # Producer
    task = ExampleTask(data="test", priority=Priority.HIGH)
    await task.push()



    queue = ExampleTask.queue()

    # Consumer
    runner = Runner(task_classes=queue.)
    runner.start()


if __name__ == "__main__":
    asyncio.run(main())
