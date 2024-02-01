import asyncio
from typing import Optional
from time import sleep

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from beanie import Document, Indexed, init_beanie
from beanie_batteries_queue import Task, State, Queue
from beanie_batteries_queue.worker import Worker
from beanie_batteries_queue.runner import Runner
from beanie_batteries_queue.scheduled_task import ScheduledTask


class Category(BaseModel):
    name: str
    description: str


class Product(Document):
    name: str                          # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: Indexed(float)              # You can also specify that a field should correspond to an index
    category: Category                 # You can include pydantic models as well





class SimpleTask(Task):
    s: str = ""
    async def run(self):
        # Implement the logic for processing the task
        
        print(f"Processing task with data: {self.s}")
        self.s = self.s.upper()
        await self.save()

    
class ProcessTask(Task):
    data: str

    async def run(self):
        self.data = self.data.upper()
        await self.save()

class AnotherTask(Task):
    data: str

    async def run(self):
        self.data = self.data.upper()
        await self.save()




# This is an asynchronous example, so we will access it from an async function
async def example():
    # Beanie uses Motor async client under the hood 
    client = AsyncIOMotorClient("mongodb://localhost:27017")

    # Initialize beanie with the Product document class
    await init_beanie(database=client.db_name, document_models=[Product,
                                                                SimpleTask,
                                                                ProcessTask,
                                                                AnotherTask,
                                                                ScheduledTask
                                                                ])

    

    # Producer
    task = SimpleTask(s="test SimpleTask")
    await task.push()
    
    task = ProcessTask(data="test ProcessTask")
    await task.push()
    
    task = AnotherTask(data="test AnotherTask")
    await task.push()

    # Consumer
    runner = Runner(task_classes=[AnotherTask])
    runner.start()
    #asyncio.create_task(await worker.start())

    
    #worker = Worker(task_classes=[ProcessTask, AnotherTask])
    #await worker.start()
    #asyncio.create_task(await worker.start())

    #sleep(10)
    #asyncio.create_task(queue.start())
    print("Task is finished")


if __name__ == "__main__":
    asyncio.run(example())
    print("Done")
