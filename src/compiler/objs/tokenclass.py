
from dataclasses import dataclass
from compiler.objs.location import Location, L
#from .location import Location, L
import typing

@dataclass
class Token:
    """Token"""
    text: str = ''
    type: str = ''
    loc: typing.Any = None
        
    def __str__(self) -> str:
        as_string = f'<Token:{self.text};{self.type};{str(self.loc)}>'
        return as_string
    
    def __post_init__(self) -> None:
        if self.loc == None:
            self.loc = L
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        text_equal = self.text == other.text
        type_equal = self.type == other.type
        loc_equal = self.loc == other.loc
        return text_equal and type_equal and loc_equal
