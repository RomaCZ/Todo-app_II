import asyncio
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from beanie import Document, Indexed, init_beanie


class Category(BaseModel):
    name: str
    description: str


class Product(Document):
    name: str                          # You can use normal types just like in pydantic
    description: Optional[str] = None
    price: Indexed(float)              # You can also specify that a field should correspond to an index
    category: Category                 # You can include pydantic models as well


from beanie_batteries_queue import Task, Runner, State
from time import sleep


class SimpleTask(Task):
    s: str = ""
    sleep(5)
    async def run(self):
        # Implement the logic for processing the task
        
        print(f"Processing task with data: {self.s}")
        self.s = self.s.upper()
        await self.save()

    





# This is an asynchronous example, so we will access it from an async function
async def example():
    # Beanie uses Motor async client under the hood 
    client = AsyncIOMotorClient("mongodb://localhost:27017")

    # Initialize beanie with the Product document class
    await init_beanie(database=client.db_name, document_models=[Product, SimpleTask])

    chocolate = Category(name="Chocolate", description="A preparation of roasted and ground cacao seeds.")
    # Beanie documents work just like pydantic models
    tonybar = Product(name="Tony's", price=5.95, category=chocolate)
    # And can be inserted into the database
    await tonybar.insert() 

    # You can find documents with pythonic syntax
    product = await Product.find_one(Product.price < 10)

    # And update them
    await product.set({Product.name:"Gold bar"})


    # Producer
    task = SimpleTask(s="test")
    await task.push()

    # Consumer
    async for task in SimpleTask.queue():
        assert task.s == "test"
        # Do some work
        await task.finish()
        break

    # Check that the task is finished
    task = await SimpleTask.find_one({"s": "test"})
    assert task.state == State.FINISHED
    
    queue = SimpleTask.queue()
    #await 
    asyncio.create_task(queue.start())
    print("Task is finished")


if __name__ == "__main__":
    asyncio.run(example())
    print("Done")
