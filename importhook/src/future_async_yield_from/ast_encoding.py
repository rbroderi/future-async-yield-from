"""
future-async-yield-from codec:
Enables:

    async yield from <expr>

inside async generator functions by expanding it into an explicit
async-delegation block (await __anext__, await asend, etc).

Used via:

  automatic import hook (importhook.py)
"""

from __future__ import annotations

import ast
import sys
from collections.abc import Sequence

import tokenize_rt  # type: ignore[import-untyped]


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
    ### AUTOGEN FROM ayf.py START - DO NOT EDIT
    # Generated: 2025-11-23 16:38:35
    try_initial = ast.Try(
        body=[
            ast.Assign(
                targets=[
                    ast.Name(
                        id='__async_yf_current',
                        ctx=ast.Store(),
                    ),
                ],
                value=ast.Await(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(
                                id='__async_yf_source',
                                ctx=ast.Load(),
                            ),
                            attr='__anext__',
                            ctx=ast.Load(),
                        ),
                    ),
                ),
            ),
        ],
        handlers=[
            ast.ExceptHandler(
                type=ast.Name(
                    id='StopAsyncIteration',
                    ctx=ast.Load(),
                ),
                body=[
                    ast.Return(),
                ],
            ),
        ],
        orelse=[
            ast.While(
                test=ast.Constant(
                    value=True,
                ),
                body=[
                    ast.Try(
                        body=[
                            ast.Assign(
                                targets=[
                                    ast.Name(
                                        id='__async_yf_sent_in',
                                        ctx=ast.Store(),
                                    ),
                                ],
                                value=ast.Yield(
                                    value=ast.Name(
                                        id='__async_yf_current',
                                        ctx=ast.Load(),
                                    ),
                                ),
                            ),
                        ],
                        handlers=[
                            ast.ExceptHandler(
                                type=ast.Name(
                                    id='GeneratorExit',
                                    ctx=ast.Load(),
                                ),
                                name='__async_yf_ge',
                                body=[
                                    ast.Try(
                                        body=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id='__async_yf_aclose',
                                                        ctx=ast.Store(),
                                                    ),
                                                ],
                                                value=ast.Attribute(
                                                    value=ast.Name(
                                                        id='__async_yf_source',
                                                        ctx=ast.Load(),
                                                    ),
                                                    attr='aclose',
                                                    ctx=ast.Load(),
                                                ),
                                            ),
                                        ],
                                        handlers=[
                                            ast.ExceptHandler(
                                                type=ast.Name(
                                                    id='AttributeError',
                                                    ctx=ast.Load(),
                                                ),
                                                body=[
                                                    ast.Pass(),
                                                ],
                                            ),
                                        ],
                                        orelse=[
                                            ast.Expr(
                                                value=ast.Await(
                                                    value=ast.Call(
                                                        func=ast.Name(
                                                            id='__async_yf_aclose',
                                                            ctx=ast.Load(),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ],
                                    ),
                                    ast.Raise(
                                        exc=ast.Name(
                                            id='__async_yf_ge',
                                            ctx=ast.Load(),
                                        ),
                                    ),
                                ],
                            ),
                            ast.ExceptHandler(
                                type=ast.Name(
                                    id='BaseException',
                                    ctx=ast.Load(),
                                ),
                                name='__async_yf_exc',
                                body=[
                                    ast.Assign(
                                        targets=[
                                            ast.Name(
                                                id='__async_yf_athrow',
                                                ctx=ast.Store(),
                                            ),
                                        ],
                                        value=ast.Call(
                                            func=ast.Name(
                                                id='getattr',
                                                ctx=ast.Load(),
                                            ),
                                            args=[
                                                ast.Name(
                                                    id='__async_yf_source',
                                                    ctx=ast.Load(),
                                                ),
                                                ast.Constant(
                                                    value='athrow',
                                                ),
                                                ast.Constant(
                                                    value=None,
                                                ),
                                            ],
                                        ),
                                    ),
                                    ast.If(
                                        test=ast.Compare(
                                            left=ast.Name(
                                                id='__async_yf_athrow',
                                                ctx=ast.Load(),
                                            ),
                                            ops=[
                                                ast.Is(),
                                            ],
                                            comparators=[
                                                ast.Constant(
                                                    value=None,
                                                ),
                                            ],
                                        ),
                                        body=[
                                            ast.Raise(),
                                        ],
                                    ),
                                    ast.Try(
                                        body=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id='__async_yf_current',
                                                        ctx=ast.Store(),
                                                    ),
                                                ],
                                                value=ast.Await(
                                                    value=ast.Call(
                                                        func=ast.Name(
                                                            id='__async_yf_athrow',
                                                            ctx=ast.Load(),
                                                        ),
                                                        args=[
                                                            ast.Name(
                                                                id='__async_yf_exc',
                                                                ctx=ast.Load(),
                                                            ),
                                                        ],
                                                    ),
                                                ),
                                            ),
                                        ],
                                        handlers=[
                                            ast.ExceptHandler(
                                                type=ast.Name(
                                                    id='StopAsyncIteration',
                                                    ctx=ast.Load(),
                                                ),
                                                body=[
                                                    ast.Return(),
                                                ],
                                            ),
                                        ],
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
                                                id='__async_yf_sent_in',
                                                ctx=ast.Load(),
                                            ),
                                            ops=[
                                                ast.Is(),
                                            ],
                                            comparators=[
                                                ast.Constant(
                                                    value=None,
                                                ),
                                            ],
                                        ),
                                        body=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id='__async_yf_current',
                                                        ctx=ast.Store(),
                                                    ),
                                                ],
                                                value=ast.Await(
                                                    value=ast.Call(
                                                        func=ast.Attribute(
                                                            value=ast.Name(
                                                                id='__async_yf_source',
                                                                ctx=ast.Load(),
                                                            ),
                                                            attr='__anext__',
                                                            ctx=ast.Load(),
                                                        ),
                                                    ),
                                                ),
                                            ),
                                        ],
                                        orelse=[
                                            ast.Assign(
                                                targets=[
                                                    ast.Name(
                                                        id='__async_yf_asend',
                                                        ctx=ast.Store(),
                                                    ),
                                                ],
                                                value=ast.Call(
                                                    func=ast.Name(
                                                        id='getattr',
                                                        ctx=ast.Load(),
                                                    ),
                                                    args=[
                                                        ast.Name(
                                                            id='__async_yf_source',
                                                            ctx=ast.Load(),
                                                        ),
                                                        ast.Constant(
                                                            value='asend',
                                                        ),
                                                        ast.Constant(
                                                            value=None,
                                                        ),
                                                    ],
                                                ),
                                            ),
                                            ast.If(
                                                test=ast.Compare(
                                                    left=ast.Name(
                                                        id='__async_yf_asend',
                                                        ctx=ast.Load(),
                                                    ),
                                                    ops=[
                                                        ast.Is(),
                                                    ],
                                                    comparators=[
                                                        ast.Constant(
                                                            value=None,
                                                        ),
                                                    ],
                                                ),
                                                body=[
                                                    ast.Assign(
                                                        targets=[
                                                            ast.Name(
                                                                id='__async_yf_current',
                                                                ctx=ast.Store(),
                                                            ),
                                                        ],
                                                        value=ast.Await(
                                                            value=ast.Call(
                                                                func=ast.Attribute(
                                                                    value=ast.Name(
                                                                        id='__async_yf_source',
                                                                        ctx=ast.Load(),
                                                                    ),
                                                                    attr='__anext__',
                                                                    ctx=ast.Load(),
                                                                ),
                                                            ),
                                                        ),
                                                    ),
                                                ],
                                                orelse=[
                                                    ast.Assign(
                                                        targets=[
                                                            ast.Name(
                                                                id='__async_yf_current',
                                                                ctx=ast.Store(),
                                                            ),
                                                        ],
                                                        value=ast.Await(
                                                            value=ast.Call(
                                                                func=ast.Name(
                                                                    id='__async_yf_asend',
                                                                    ctx=ast.Load(),
                                                                ),
                                                                args=[
                                                                    ast.Name(
                                                                        id='__async_yf_sent_in',
                                                                        ctx=ast.Load(),
                                                                    ),
                                                                ],
                                                            ),
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                                handlers=[
                                    ast.ExceptHandler(
                                        type=ast.Name(
                                            id='StopAsyncIteration',
                                            ctx=ast.Load(),
                                        ),
                                        body=[
                                            ast.Return(),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    ### AUTOGEN FROM ayf.py STOP - DO NOT EDIT
    return [assign_source, try_initial]


# CUSTOM AST MARKER NODE
class AsyncYieldFrom(ast.AST):
    _fields = ("value",)

    def __init__(self, value: ast.expr) -> None:
        super().__init__()
        self.value = value


class AsyncYieldFromExpander(ast.NodeTransformer):
    def visit_AsyncYieldFrom(self, node: AsyncYieldFrom) -> list[ast.stmt]:
        return make_async_yield_from_ast(node.value)


def rewrite_async_yield_from(
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

    def _skip_ws(idx: int) -> int:
        """Advance idx until a non-whitespace token (keeps indentation intact)."""
        while idx < len(tokens) and tokens[idx].name == "UNIMPORTANT_WS":
            idx += 1
        return idx

    new_tokens: list[tokenize_rt.Token] = []
    i = 0

    while i < len(tokens):
        tok = tokens[i]
        # async yield from
        if tok.src == "async":
            yield_idx = _skip_ws(i + 1)
            if yield_idx >= len(tokens) or tokens[yield_idx].src != "yield":
                new_tokens.append(tok)
                i += 1
                continue

            from_idx = _skip_ws(yield_idx + 1)
            if from_idx >= len(tokens) or tokens[from_idx].src != "from":
                new_tokens.append(tok)
                i += 1
                continue

            expr_start = _skip_ws(from_idx + 1)
            expr_end = expr_start

            # Collect expression tokens until newline/semicolon
            while expr_end < len(tokens):
                t = tokens[expr_end]
                if t.name in ("NEWLINE", "NL", "ENDMARKER") or t.src == ";":
                    break
                expr_end += 1

            expr_src = tokenize_rt.tokens_to_src(tokens[expr_start:expr_end]).strip()

            expr_ast = ast.parse(expr_src, mode="eval").body
            expansion = make_async_yield_from_ast(expr_ast)
            module = ast.Module(body=expansion, type_ignores=[])
            ast.fix_missing_locations(module)
            block_src = ast.unparse(module).strip("\n")

            indent_parts: list[str] = []
            while new_tokens and new_tokens[-1].name in {"INDENT", "UNIMPORTANT_WS"}:
                candidate = new_tokens[-1]
                if "\n" in candidate.src:
                    break
                indent_parts.append(new_tokens.pop().src)
            base_indent = "".join(reversed(indent_parts))
            if not base_indent:
                column_raw = getattr(
                    tok.offset, "utf8_byte_offset", tok.utf8_byte_offset
                )
                column = int(column_raw or 0)
                base_indent = " " * column

            indented_block = "\n".join(
                (base_indent + line if line else line)
                for line in block_src.splitlines()
            )
            replacement_src = indented_block + "\n"
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


def _dev_build() -> None:
    import re
    from datetime import datetime
    from pathlib import Path

    from asttab import ASTParser

    UUID = "f717423b-daae-4070-9eb6-e7fe1ff8b74f"
    if not (Path(__file__).parent.parent.parent.parent / UUID).exists():
        return
    print("dev uuid file found running autogen...")
    ## self modifying code - updates the AUTOGEN section above
    # Read the ayf.py file from the same directory as the UUID file
    ayf_file = Path(__file__).parent.parent.parent.parent / "ayf.py"
    if not ayf_file.exists():
        print(f"Error: {ayf_file} not found")
        sys.exit(1)

    # Read the ayf.py source code and locate the async_yield_from() body
    ayf_source = ayf_file.read_text()
    ayf_module = ast.parse(ayf_source)
    async_func = next(
        (
            node
            for node in ayf_module.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_yield_from"
        ),
        None,
    )
    if async_func is None:
        print("Error: async_yield_from() not found in ayf.py")
        sys.exit(1)
    try_block = next(
        (stmt for stmt in async_func.body if isinstance(stmt, ast.Try)),
        None,
    )
    if try_block is None:
        print("Error: async_yield_from() missing leading try block")
        sys.exit(1)

    try_dump = ast.dump(try_block, indent=4)
    builder_expr = ASTParser(try_dump).parse(pretty=True)
    builder_expr = f"try_initial = {builder_expr}"
    if not builder_expr.endswith("\n"):
        builder_expr += "\n"

    # Read current file
    current_file = Path(__file__)
    current_content = current_file.read_text()

    # Indent the builder code to match the function's indentation (4 spaces)
    indented_ast_code = "\n".join(
        "    " + line if line.strip() else line for line in builder_expr.split("\n")
    )

    # Find and replace the AUTOGEN section
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pattern = r"(### AUTOGEN FROM ayf\.py START - DO NOT EDIT\n)(.*?)(### AUTOGEN FROM ayf\.py STOP - DO NOT EDIT)"

    replacement = f"\\g<1>    # Generated: {timestamp}\n{indented_ast_code}\n    \\g<3>"

    new_content = re.sub(pattern, replacement, current_content, flags=re.DOTALL)

    # Write back to file
    current_file.write_text(new_content)
    print(f"Updated AUTOGEN section in {current_file}")


if __name__ == "__main__":
    _dev_build()
