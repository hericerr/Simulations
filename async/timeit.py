import time

def timeit(func):
	"""Decorator to print time elapsed during function execution"""
	def timed(*args, **kwargs):
		start = time.perf_counter()
		res = func(*args, **kwargs)
		print(f'{func.__name__} run in: {time.perf_counter() - start}')
		return res
	return timed


def async_timeit(func):
	"""Asynchronous version of timeit"""
	async def timed(*args, **kwargs):
		start = time.perf_counter()
		res = await func(*args, **kwargs)
		print(f'{func.__name__} run in: {time.perf_counter() - start}')
		return res
	return timed