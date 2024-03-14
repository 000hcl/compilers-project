from dataclasses import dataclass, field
from compiler.objs.location import Location
from compiler.objs.types import Type, Unit

@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    location: Location | None
    type: Type = field(kw_only=True, default=Unit)

@dataclass
class Literal(Expression):
    value: int | bool | None
    # (value=None is used when parsing the keyword `unit`)

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class TypeExpr:
    """Base class for type expressions."""
    variable: Identifier
    location: Location

@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

@dataclass
class IfThenElse(Expression):
    """AST node for if else then, else optional"""
    condition: Expression
    then_branch: Expression
    else_branch: Expression | None

@dataclass
class FunctionNode(Expression):
    function: Identifier
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
    dec_type: TypeExpr | None = None

@dataclass
class Loop(Expression):
    while_exp: Expression
    do_exp: Expression

@dataclass
class Assignment(Expression):
    left: Expression
    right: Expression





@dataclass
class SimpleType(TypeExpr):
    type_name: str

@dataclass
class TypeFunction(TypeExpr):
    parameters: list[TypeExpr]
    result: TypeExpr
    