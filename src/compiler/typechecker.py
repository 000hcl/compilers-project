from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class SymTab:
    locals: dict = field(default_factory=dict)
    parent: SymTab | None = None
    
    def get_type(self, var: str):
        local_type = self.locals.get(var)
        if not local_type:
            if isinstance(self.parent, None):
                raise Exception(f'Variable "{var}" not declared.')
            return self.parent.get_type(var)
        else:
            return local_type



