import asyncio
import inspect


def simple_decorator(func):
    async def wrapper(*args, **kwargs):
        # Call func to get the underlying async generator / async iterable
        __async_yf_source = func(*args, **kwargs)
        try:
            __async_yf_current = await __async_yf_source.__anext__()
        except StopAsyncIteration:
            return
        else:
            while True:
                try:
                    __async_yf_sent_in = yield __async_yf_current
                except BaseException as __async_yf_exc:
                    __async_yf_athrow = getattr(__async_yf_source, "athrow", None)
                    if __async_yf_athrow is None:
                        raise
                    try:
                        __async_yf_current = await __async_yf_athrow(__async_yf_exc)
                    except StopAsyncIteration:
                        return
                else:
                    try:
                        if __async_yf_sent_in is None:
                            __async_yf_current = await __async_yf_source.__anext__()
                        else:
                            __async_yf_asend = getattr(__async_yf_source, "asend", None)
                            if __async_yf_asend is None:
                                __async_yf_current = await __async_yf_source.__anext__()
                            else:
                                __async_yf_current = await __async_yf_asend(
                                    __async_yf_sent_in
                                )
                    except StopAsyncIteration:
                        return

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
