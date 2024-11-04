import threading 
import asyncio 

async def foo():
    await asyncio.sleep(1)
    print("foo")

