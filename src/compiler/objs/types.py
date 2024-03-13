from dataclasses import dataclass

class Type:
    """Base class for types"""

class IntegerType(Type):
    """Class for integers."""

class BooleanType(Type):
    """Class for booleans."""

@dataclass
class FunType(Type):
    """Class for functions."""
    parameters: list[Type]
    result: Type

class UnitType(Type):
    """Class for unit."""

Int = IntegerType()
Bool = BooleanType()
Unit = UnitType()