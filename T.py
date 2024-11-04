import threading
import asyncio
import time

def heavy_computing():
    # Simulate a heavy computation
    for i in range(200000000):
        pass
    return 1

def run_asyncio_in_thread(i):
    # Define the asynchronous coroutine
    async def foo():
        print(f"Sleeping foo {i}")
        await asyncio.sleep(0.1)
        print(f'Starting foo {i}')
        heavy_computing()
        print(f'Finished foo {i}')

    # Create a new event loop in this thread and run the coroutine
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(foo())
    loop.close()

def main():
    threads = []
    for i in range(3):
        # Start a new thread for each asyncio coroutine
        t = threading.Thread(target=run_asyncio_in_thread, args=(i,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

start = time.time()
main()
print(f"Total time: {time.time() - start}")

start = time.time()
for _ in range(3):
    heavy_computing()
print(f"Total time: {time.time() - start}")



