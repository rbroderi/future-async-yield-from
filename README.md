WARNING: Here there be dragons!! Extremely untested code

Adds the syntax 'async yield from' to python

implements yield from in a async case via pure python
see PEP 380

there are two ways to integrate into python, via a importhook and an encoding string.

The importhook effects all files after its install - it modifies all files at import time.

the encoding string is probably safer as its opt in - requires the file to have the encoding string specifier, and then it can use the new "async yield from" syntax.

based on

```python
# -*- coding: future-async-yield-from -*-
# above is only required if using the encoding string version.
from __future__ import annotations
import inspect
import asyncio
from beartype import beartype

def beariertype(func):
    func=beartype(func)
    async def wrapper(*args, **kwargs):
        # Call func to get the underlying async generator / async iterable
        async yield from func(*args, **kwargs)
    return wrapper


@beariertype
async def a_gen(x: int):
    yield x


print(inspect.isasyncgenfunction(a_gen))  # should be True


async def main():
    async for value in a_gen(1):
        print("ok:", value) # ok

    async for value in a_gen("bad"):
        print("bad:", value) # beartype error


asyncio.run(main())
```




