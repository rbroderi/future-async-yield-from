import re

ASYNC_YF = re.compile(
    r"^(?P<indent>[ \t]*)async[ \t]+yield[ \t]+from[ \t]+(?P<expr>.+)$",
    re.MULTILINE,
)

DELEGATION_TEMPLATE = """{i}__async_yf_source = {e}
{i}try:
{i}    __async_yf_current = await __async_yf_source.__anext__()
{i}except StopAsyncIteration:
{i}    return
{i}else:
{i}    while True:
{i}        try:
{i}            __async_yf_sent_in = yield __async_yf_current
{i}        except BaseException as __async_yf_exc:
{i}            __async_yf_athrow = getattr(__async_yf_source, "athrow", None)
{i}            if __async_yf_athrow is None:
{i}                raise
{i}            try:
{i}                __async_yf_current = await __async_yf_athrow(__async_yf_exc)
{i}            except StopAsyncIteration:
{i}                return
{i}        else:
{i}            try:
{i}                if __async_yf_sent_in is None:
{i}                    __async_yf_current = await __async_yf_source.__anext__()
{i}                else:
{i}                    __async_yf_asend = getattr(__async_yf_source, "asend", None)
{i}                    if __async_yf_asend is None:
{i}                        __async_yf_current = await __async_yf_source.__anext__()
{i}                    else:
{i}                        __async_yf_current = await __async_yf_asend(__async_yf_sent_in)
{i}            except StopAsyncIteration:
{i}                return
"""


def rewrite(src: str) -> str:
    """Rewrite `async yield from expr` into full delegation."""

    def repl(m):
        indent = m.group("indent")
        expr = m.group("expr")
        return DELEGATION_TEMPLATE.format(i=indent, e=expr)

    return ASYNC_YF.sub(repl, src)
