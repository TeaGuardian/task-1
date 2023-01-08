import ast, astunparse

with open('1.py') as f:
    lines = astunparse.unparse(ast.parse(f.read())).split('\n')
    for line in lines:
        if line.lstrip()[:1] not in ("'", '"'):
            print(line)