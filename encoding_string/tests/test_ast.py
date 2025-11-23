# -*- coding: future-async-yield-from -*-
import inspect
import asyncio
from beartype import beartype

def simple_decorator(func):
    func=beartype(func)
    async def wrapper(*args, **kwargs):
        # Call func to get the underlying async generator / async iterable
        async yield from func(*args, **kwargs)
    return wrapper


@simple_decorator
async def a_gen(x: int):
    yield x


print(inspect.isasyncgenfunction(a_gen))  # should be True


async def main():
    async for value in a_gen(1):
        print("ok:", value)

    # This will blow up at *runtime* because  "bad" isn't the right type,
    # but that's separate from the codec working.
    async for value in a_gen("bad"):
        print("bad:", value)


asyncio.run(main())
