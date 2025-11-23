from future_async_yield_from.ast_encoding import decode, register

register()

with open(
    r"C:\Users\richa\workspace_local\future-async-yield-from\tests\test_ast.py",
    "rb",
) as f:
    text, _ = decode(f.read())

print(text)
# exec(text)
