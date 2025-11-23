import asyncio
import inspect

import pytest
from beartype.roar import BeartypeCallHintParamViolation

from tests.async_fixture import a_gen


def test_is_async_generator_function():
    assert inspect.isasyncgenfunction(a_gen)


def test_async_iteration_emits_values():
    async def _runner():
        observed: list[int] = []
        async for value in a_gen(1):
            observed.append(value)
        return observed

    assert asyncio.run(_runner()) == [1]


def test_type_guard_enforced():
    async def _runner():
        async for _ in a_gen("bad"):
            pass

    with pytest.raises(BeartypeCallHintParamViolation):
        asyncio.run(_runner())
