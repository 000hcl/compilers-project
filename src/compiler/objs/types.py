from dataclasses import dataclass

class Type:
    """Base class for types"""

class IntegerType(Type):
    """Class for integers."""

class BooleanType(Type):
    """Class for booleans."""

class FunctionType(Type):
    """Class for functions."""

Int = IntegerType()
Bool = BooleanType()
FunType = FunctionType()