import os
import time
import asyncio
from timeit import async_timeit


async def data_generator(n):
    'Get data from somewhere asynchronously'
    for i in range(n):
        await asyncio.sleep(1)
        yield(os.urandom(5).hex())

async def producer(name, q, n=3):
    'Get data from generator and put them to queue'
    async for data in data_generator(n):
        await q.put(data)
        print(f'Producer {name} added {data} into queue')

async def worker(name, q):
    'Get data from queue, do some CPU intensive work and then write it somewhere asynchronously'
    while True:
        data = await q.get()
        print(f'Worker {name} got {data}')
        # TODO: run_in_executor
        time.sleep(1)
        await asyncio.sleep(1)
        q.task_done()
        print(f'Worker {name} processed {data}')

@async_timeit
async def main():
    q = asyncio.Queue()
    producers = [asyncio.create_task(producer(n, q)) for n in range(5)]
    workers = [asyncio.create_task(worker(n, q)) for n in range(5)]
    await asyncio.gather(*producers)
    await q.join()
    for w in workers:
        w.cancel()

if __name__ == "__main__":
    asyncio.run(main())