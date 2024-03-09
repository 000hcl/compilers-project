from dataclasses import dataclass
from compiler.objs.location import Location

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    location: Location | None

@dataclass
class Literal(Expression):
    value: int | bool | None
    # (value=None is used when parsing the keyword `unit`)

@dataclass
class Identifier(Expression):
    name: str
    type: None = None

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

@dataclass
class ControlNode(Expression):
    """AST node for if else then, else optional"""
    if_exp: Expression
    then_exp: Expression
    else_exp: Expression | None

@dataclass
class FunctionNode(Expression):
    function: Expression
    arguments: list[Expression]

@dataclass
class UnaryOp(Expression):
    op: str
    element: Expression

@dataclass
class Block(Expression):
    expressions: list[Expression]
    result: Expression

@dataclass
class VarDec(Expression):
    name: Identifier
    value: Expression

@dataclass
class Loop(Expression):
    while_exp: Expression
    do_exp: Expression