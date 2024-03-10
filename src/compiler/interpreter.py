from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, TypeAlias, TypeVar

from compiler import ast

Value:TypeAlias = int | bool | None

@dataclass
class SymTab:
    locals: dict = field(default_factory=dict)
    parent: SymTab | None = None

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
                if isinstance(node.else_branch, ast.Expression):
                    return interpret(node.else_branch)
                else:
                    return None


    raise Exception('Unexpected node')
