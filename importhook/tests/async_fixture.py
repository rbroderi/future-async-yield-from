from beartype import beartype


def simple_decorator(func):
    func = beartype(func)

    async def wrapper(*args, **kwargs):
        # Call func to get the underlying async generator / async iterable
        async yield from func(*args, **kwargs)

    return wrapper


@simple_decorator
async def a_gen(x: int):
    yield x
