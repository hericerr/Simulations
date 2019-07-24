import asyncio
from timeit import timeit

async def hello_world():
		print('Hello')
		await asyncio.sleep(1)
		print('world!')

async def hello_worlds1(n):
	await asyncio.gather(*(hello_world() for _ in range(n)))

@timeit
def main_hello_worlds():
	asyncio.run(hello_worlds1(3))


async def hello():
	await asyncio.sleep(0.5)
	return 'Hello'

async def world():
	await asyncio.sleep(0.5)
	return 'world!'
	
async def hello_world_parts():
	h = await hello()
	w = await world()
	print(f'{h} {w}')
		
async def hello_worlds2(n):
	await asyncio.gather(*(hello_world_parts() for _ in range(n)))
	
@timeit
def main_hello_worlds2():
	asyncio.run(hello_worlds2(3))
	

async def hello_generator(n):
	i = 0
	await asyncio.sleep(1)
	while i < n:
		yield 'Hello'
		i += 1
		
async def world_generator(n):
	i = 0
	await asyncio.sleep(1)
	while i < n:
		yield 'world!'
		i += 1
		
async def generate_hellos(n):
	async for h in hello_generator(n):
		print(h)
		
async def generate_worlds(n):
	async for w in world_generator(n):
		print(w)
		
async def print_hello_worlds(n):
	await asyncio.gather(generate_hellos(n), generate_worlds(n))

@timeit
def main_hello_worlds3():
	asyncio.run(print_hello_worlds(3))
	

if __name__ == '__main__':
	print('Hello the world of asynchronous programming!')
	print('')
	main_hello_worlds()
	print('')
	main_hello_worlds2()
	print('')
	main_hello_worlds3()