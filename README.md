WARNING: Here there be dragons!! Extremely untested code

Adds the syntax 'async yield from' to python

implements yield from in a async case via pure python
see PEP 380

based on

```python
from __future__ import annotations

import inspect
from collections.abc import AsyncGenerator
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec
from typing import TypeVar

from beartype import beartype

_P = ParamSpec("_P")
_TYield = TypeVar("_TYield")
_TSend = TypeVar("_TSend")


def preserve_asyncgen(
    asyncgen_func: Callable[_P, AsyncGenerator[_TYield, _TSend]],
) -> Callable[_P, AsyncGenerator[_TYield, _TSend]]:
    """Restores async-generator semantics after wrapping.

    It delegates iteration, send(), throw(), and close() to the underlying
    async generator `asyncgen_func`, preserving correct async generator behavior.
    """

    @wraps(asyncgen_func)
    async def wrapper(
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AsyncGenerator[_TYield, _TSend]:
        # Call the underlying async generator function.
        source_agen: AsyncGenerator[_TYield, _TSend] = asyncgen_func(*args, **kwargs)

        try:
            # Prime the generator: get its first yielded value.
            current_value: _TYield = await source_agen.__anext__()
        except StopAsyncIteration:
            # Underlying generator produced nothing.
            return
        else:
            while True:
                try:
                    # Yield value to caller, await next "sent" value back in.
                    sent_in: _TSend | None = yield current_value

                except BaseException as raised_exc:
                    # Attempt to forward exception into underlying generator.
                    athrow = getattr(source_agen, "athrow", None)
                    if athrow is None:
                        # Underlying generator cannot accept exceptions.
                        raise

                    try:
                        current_value = await athrow(raised_exc)
                    except StopAsyncIteration:
                        return

                else:
                    # No exception: either a .send(value) or pure "next".
                    try:
                        if sent_in is None:
                            # Regular iteration
                            current_value = await source_agen.__anext__()
                        else:
                            # Value sent into the generator
                            asend = getattr(source_agen, "asend", None)
                            if asend is None:
                                # Underlying generator cannot receive values
                                current_value = await source_agen.__anext__()
                            else:
                                current_value = await asend(sent_in)

                    except StopAsyncIteration:
                        return

    return wrapper


@preserve_asyncgen
@beartype
async def a_gen(x: int):
    yield x


print(inspect.isasyncgenfunction(a_gen))  # True 🎉
import asyncio


async def main():
    async for value in a_gen(1):  # works
        print(value)
    async for value in a_gen("bad"):  # beartype param violation here
        print(value)


asyncio.run(main())
```
Simplified version by https://github.com/Glinte: (assumes async generator)
```python
def preserve_asyncgen(
    asyncgen_func: Callable[_P, AsyncGenerator[_TYield, _TSend]],
) -> Callable[_P, AsyncGenerator[_TYield, _TSend]]:
    """Restores async-generator semantics after wrapping.

    It delegates iteration, send(), throw(), and close() to the underlying
    async generator `asyncgen_func`, preserving correct async generator behavior.
    """

    @wraps(asyncgen_func)
    async def wrapper(
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AsyncGenerator[_TYield, _TSend]:
        # Call the underlying async generator function.
        source_agen: AsyncGenerator[_TYield, _TSend] = asyncgen_func(*args, **kwargs)

        # Localize async generator methods for efficiency.
        athrow = source_agen.athrow
        asend = source_agen.asend
        anext = source_agen.__anext__

        try:
            # Prime the generator: get its first yielded value.
            current_value = await anext()
        except StopAsyncIteration:
            # Underlying generator produced nothing.
            return
        else:
            while True:
                try:
                    # Yield value to caller, await next "sent" value back in.
                    sent_in = yield current_value

                except BaseException as raised_exc:
                    # Forward exception into underlying generator.
                    try:
                        current_value = await athrow(raised_exc)
                    except StopAsyncIteration:
                        return

                else:
                    # No exception: either a .send(value) or pure "next".
                    try:
                        if sent_in is None:
                            # Regular iteration
                            current_value = await anext()
                        else:
                            # Value sent into the generator
                            current_value = await asend(sent_in)

                    except StopAsyncIteration:
                        return

    return wrapper
```

