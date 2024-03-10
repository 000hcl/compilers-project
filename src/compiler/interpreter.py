from typing import Any, TypeAlias
from compiler import ast

Value:TypeAlias = int | bool | None
"""
def interpret(node: ast.Expression) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
            if node.op == '+':
                return a + b
            elif node.op == '<':
                return a < b
            else:
                raise Exception('exp')

        case ast.IfThenElse():
            if interpret(node.condition):
                return interpret(node.then_branch)
            else:
                return interpret(node.else_branch)

"""