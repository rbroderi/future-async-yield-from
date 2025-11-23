"""
future-async-yield-from codec:
Enables:

    async yield from <expr>

inside async generator functions by expanding it into an explicit
async-delegation block (await __anext__, await asend, etc).

Used via:

    # -*- coding: future-async-yield-from -*-
"""

from __future__ import annotations

import argparse
import ast
import codecs
import encodings
import sys
from collections.abc import Buffer, Sequence
from typing import IO

import tokenize_rt  # type: ignore[import-untyped]

# Base UTF-8 codec used for decoding before rewriting tokens
utf_8 = encodings.search_function("utf8")
if utf_8 is None:
    raise RuntimeError("unable to find utf8 encoding function.")


def make_async_yield_from_ast(expr: ast.expr) -> list[ast.stmt]:
    """
    Return the AST block that implements:

        async yield from <expr>

    expanded into the full try/while/try/await/yield form.
    """
    assign_source = ast.Assign(
        targets=[ast.Name(id="__async_yf_source", ctx=ast.Store())],
        value=expr,
    )

    try_initial = ast.Try(
        body=[
            ast.Assign(
                targets=[ast.Name(id="__async_yf_current", ctx=ast.Store())],
                value=ast.Await(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="__async_yf_source", ctx=ast.Load()),
                            attr="__anext__",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    )
                ),
            )
        ],
        handlers=[
            ast.ExceptHandler(
                type=ast.Name(id="StopAsyncIteration", ctx=ast.Load()),
                name=None,
                body=[ast.Return()],
            )
        ],
        orelse=[
            ast.While(
                test=ast.Constant(True),
                body=[
                    ast.Try(
                        body=[
                            ast.Assign(
                                targets=[
                                    ast.Name(id="__async_yf_sent_in", ctx=ast.Store())
                                ],
                                value=ast.Yield(
                                    value=ast.Name(
                                        id="__async_yf_current", ctx=ast.Load()
                                    )
                                ),
                            )
                        ],
                        handlers=[
                            ast.ExceptHandler(
                                type=ast.Name(id="GeneratorExit", ctx=ast.Load()),
                                name="__async_yf_ge",
                                body=[
                                    ast.Try(
                                        body=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id="__async_yf_aclose",
                                                        ctx=ast.Store(),
                                                    )
                                                ],
                                                value=ast.Attribute(
                                                    value=ast.Name(
                                                        id="__async_yf_source",
                                                        ctx=ast.Load(),
                                                    ),
                                                    attr="aclose",
                                                    ctx=ast.Load(),
                                                ),
                                            )
                                        ],
                                        handlers=[
                                            ast.ExceptHandler(
                                                type=ast.Name(
                                                    id="AttributeError", ctx=ast.Load()
                                                ),
                                                name=None,
                                                body=[ast.Pass()],
                                            )
                                        ],
                                        orelse=[
                                            ast.Expr(
                                                value=ast.Await(
                                                    value=ast.Call(
                                                        func=ast.Name(
                                                            id="__async_yf_aclose",
                                                            ctx=ast.Load(),
                                                        ),
                                                        args=[],
                                                        keywords=[],
                                                    )
                                                )
                                            )
                                        ],
                                        finalbody=[],
                                    ),
                                    ast.Raise(
                                        exc=ast.Name(
                                            id="__async_yf_ge", ctx=ast.Load()
                                        ),
                                        cause=None,
                                    ),
                                ],
                            ),
                            ast.ExceptHandler(
                                type=ast.Name(id="BaseException", ctx=ast.Load()),
                                name="__async_yf_exc",
                                body=[
                                    ast.Assign(
                                        targets=[
                                            ast.Name(
                                                id="__async_yf_athrow", ctx=ast.Store()
                                            )
                                        ],
                                        value=ast.Call(
                                            func=ast.Name(id="getattr", ctx=ast.Load()),
                                            args=[
                                                ast.Name(
                                                    id="__async_yf_source",
                                                    ctx=ast.Load(),
                                                ),
                                                ast.Constant("athrow"),
                                                ast.Constant(None),
                                            ],
                                            keywords=[],
                                        ),
                                    ),
                                    ast.If(
                                        test=ast.Compare(
                                            left=ast.Name(
                                                id="__async_yf_athrow", ctx=ast.Load()
                                            ),
                                            ops=[ast.Is()],
                                            comparators=[ast.Constant(None)],
                                        ),
                                        body=[ast.Raise()],
                                        orelse=[],
                                    ),
                                    ast.Try(
                                        body=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id="__async_yf_current",
                                                        ctx=ast.Store(),
                                                    )
                                                ],
                                                value=ast.Await(
                                                    value=ast.Call(
                                                        func=ast.Name(
                                                            id="__async_yf_athrow",
                                                            ctx=ast.Load(),
                                                        ),
                                                        args=[
                                                            ast.Name(
                                                                id="__async_yf_exc",
                                                                ctx=ast.Load(),
                                                            )
                                                        ],
                                                        keywords=[],
                                                    )
                                                ),
                                            )
                                        ],
                                        handlers=[
                                            ast.ExceptHandler(
                                                type=ast.Name(
                                                    id="StopAsyncIteration",
                                                    ctx=ast.Load(),
                                                ),
                                                body=[ast.Return()],
                                            )
                                        ],
                                        orelse=[],
                                        finalbody=[],
                                    ),
                                ],
                            ),
                        ],
                        orelse=[
                            ast.Try(
                                body=[
                                    ast.If(
                                        test=ast.Compare(
                                            left=ast.Name(
                                                id="__async_yf_sent_in", ctx=ast.Load()
                                            ),
                                            ops=[ast.Is()],
                                            comparators=[ast.Constant(None)],
                                        ),
                                        body=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id="__async_yf_current",
                                                        ctx=ast.Store(),
                                                    )
                                                ],
                                                value=ast.Await(
                                                    value=ast.Call(
                                                        func=ast.Attribute(
                                                            value=ast.Name(
                                                                id="__async_yf_source",
                                                                ctx=ast.Load(),
                                                            ),
                                                            attr="__anext__",
                                                            ctx=ast.Load(),
                                                        ),
                                                        args=[],
                                                        keywords=[],
                                                    )
                                                ),
                                            )
                                        ],
                                        orelse=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id="__async_yf_asend",
                                                        ctx=ast.Store(),
                                                    )
                                                ],
                                                value=ast.Call(
                                                    func=ast.Name(
                                                        id="getattr", ctx=ast.Load()
                                                    ),
                                                    args=[
                                                        ast.Name(
                                                            id="__async_yf_source",
                                                            ctx=ast.Load(),
                                                        ),
                                                        ast.Constant("asend"),
                                                        ast.Constant(None),
                                                    ],
                                                    keywords=[],
                                                ),
                                            ),
                                            ast.If(
                                                test=ast.Compare(
                                                    left=ast.Name(
                                                        id="__async_yf_asend",
                                                        ctx=ast.Load(),
                                                    ),
                                                    ops=[ast.Is()],
                                                    comparators=[ast.Constant(None)],
                                                ),
                                                body=[
                                                    ast.Assign(
                                                        targets=[
                                                            ast.Name(
                                                                id="__async_yf_current",
                                                                ctx=ast.Store(),
                                                            )
                                                        ],
                                                        value=ast.Await(
                                                            value=ast.Call(
                                                                func=ast.Attribute(
                                                                    value=ast.Name(
                                                                        id="__async_yf_source",
                                                                        ctx=ast.Load(),
                                                                    ),
                                                                    attr="__anext__",
                                                                    ctx=ast.Load(),
                                                                ),
                                                                args=[],
                                                                keywords=[],
                                                            )
                                                        ),
                                                    )
                                                ],
                                                orelse=[
                                                    ast.Assign(
                                                        targets=[
                                                            ast.Name(
                                                                id="__async_yf_current",
                                                                ctx=ast.Store(),
                                                            )
                                                        ],
                                                        value=ast.Await(
                                                            value=ast.Call(
                                                                func=ast.Name(
                                                                    id="__async_yf_asend",
                                                                    ctx=ast.Load(),
                                                                ),
                                                                args=[
                                                                    ast.Name(
                                                                        id="__async_yf_sent_in",
                                                                        ctx=ast.Load(),
                                                                    )
                                                                ],
                                                                keywords=[],
                                                            )
                                                        ),
                                                    )
                                                ],
                                            ),
                                        ],
                                    )
                                ],
                                handlers=[
                                    ast.ExceptHandler(
                                        type=ast.Name(
                                            id="StopAsyncIteration", ctx=ast.Load()
                                        ),
                                        body=[ast.Return()],
                                    )
                                ],
                                orelse=[],
                                finalbody=[],
                            )
                        ],
                        finalbody=[],
                    )
                ],
                orelse=[],
            )
        ],
        finalbody=[],
    )

    return [assign_source, try_initial]


# CUSTOM AST MARKER NODE
class AsyncYieldFrom(ast.AST):
    _fields = ("value",)

    def __init__(self, value: ast.expr) -> None:
        super().__init__()
        self.value = value


class AsyncYieldFromExpander(ast.NodeTransformer):
    def visit_AsyncYieldFrom(self, node: AsyncYieldFrom):
        return make_async_yield_from_ast(node.value)


def _rewrite_async_yield_from(
    tokens: Sequence[tokenize_rt.Token],
) -> list[tokenize_rt.Token]:
    """
    Look for:   async yield from <something>
    Replace with: AsyncYieldFrom(<expr>)
    but represented as source code the AST parser will pick up.

    The codec emits:

        AsyncYieldFrom(<expr>)

    which the AST transformer later expands.
    """
    new_tokens: list[tokenize_rt.Token] = []
    i = 0

    while i < len(tokens):
        tok = tokens[i]
        # async yield from
        if (
            tok.src == "async"
            and i + 2 < len(tokens)
            and tokens[i + 1].src == "yield"
            and tokens[i + 2].src == "from"
        ):
            expr_start = i + 3
            expr_end = expr_start

            # Collect expression tokens until newline/semicolon
            while expr_end < len(tokens):
                t = tokens[expr_end]
                if t.name in ("NEWLINE", "NL", "ENDMARKER") or t.src == ";":
                    break
                expr_end += 1

            expr_src = tokenize_rt.tokens_to_src(tokens[expr_start:expr_end]).strip()

            # Replace with: AsyncYieldFrom(<expr>)
            replacement_src = f"AsyncYieldFrom({expr_src})"
            replacement_tokens = list(tokenize_rt.src_to_tokens(replacement_src))
            if replacement_tokens and replacement_tokens[0].name == "ENCODING":
                replacement_tokens = replacement_tokens[1:]

            new_tokens.extend(replacement_tokens)

            if expr_end < len(tokens):
                new_tokens.append(tokens[expr_end])

            i = expr_end + 1
            continue

        new_tokens.append(tok)
        i += 1

    return new_tokens


def decode(input: Buffer, errors: str = "strict") -> tuple[str, int]:
    """Decode UTF-8, rewrite async-yield-from, output transformed UTF-8 text."""
    b = bytes(input)
    if utf_8 is None:
        raise TypeError(" encodings.search_function('utf8') was unable to find uft8")
    u, length = utf_8.decode(b, errors)

    tokens = tokenize_rt.src_to_tokens(u)
    tokens = _rewrite_async_yield_from(tokens)
    new_src = tokenize_rt.tokens_to_src(tokens)

    return new_src, length


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(
        self, input: Buffer, errors: str, final: bool
    ) -> tuple[str, int]:
        if final:
            return decode(input, errors)
        return ("", 0)


class StreamReader(codecs.StreamReader):
    """
    UTF-8 reader that applies async-yield-from token rewrite.
    """

    def __init__(self, stream: IO[bytes], errors: str = "strict") -> None:
        super().__init__(stream, errors)

    def decode(self, input: bytes, errors: str = "strict") -> tuple[str, int]:
        return decode(input, errors)

    def read(self, size: int = -1, chars: int = -1, firstline: bool = False) -> str:
        data = super().read(size, chars, firstline)
        if not isinstance(data, bytes):
            return data
        text, _ = decode(data)
        return text

    def readline(self, size: int | None = None, keepends: bool = False) -> str:
        data = super().readline(size, keepends)
        if not isinstance(data, bytes):
            return data
        text, _ = decode(data)
        return text


def make_streamreader(stream: IO[bytes], errors: str = "strict") -> StreamReader:
    return StreamReader(stream, errors)


codec_map: dict[str, codecs.CodecInfo] = {
    name: codecs.CodecInfo(
        name=name,
        encode=utf_8.encode,
        decode=decode,
        incrementalencoder=utf_8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=make_streamreader,  # type: ignore[arg-type]
        streamwriter=utf_8.streamwriter,
    )
    for name in ("future-async-yield-from", "future_async_yield_from")
}


def register() -> None:
    codecs.register(codec_map.get)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prints transformed source.")
    parser.add_argument("filename")
    args = parser.parse_args(argv)

    with open(args.filename, "rb") as f:
        text, _ = decode(f.read())

    getattr(sys.stdout, "buffer", sys.stdout).write(text)
    return 0


# Patch base class dynamically (required for type correctness)
StreamReader.__bases__ = (utf_8.streamreader,)  # type: ignore[assignment]


if __name__ == "__main__":
    raise SystemExit(main())
