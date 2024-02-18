from dataclasses import dataclass

@dataclass
class Location(object):
    """Location"""
    file: str = 'Null'
    row: int = 0
    column: int = 0
    equal_to_all: bool = False
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Location):
            return NotImplemented
        if self.equal_to_all == True:
            return True
        if other.equal_to_all == True:
            return True
        return (self.file == other.file) and (self.row == other.row) and (self.column==other.column)
    
    def __str__(self) -> str:
        return f'<Location:{self.file};{self.row};{self.column}>'
    
L = Location(equal_to_all=True)