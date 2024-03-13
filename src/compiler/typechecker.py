from __future__ import annotations
from dataclasses import dataclass, field
from compiler.objs.types import Type, Int, Bool, FunType, Unit
import compiler.ast as ast

@dataclass
class SymTab:
    locals: dict = field(default_factory=dict)
    parent: SymTab | None = None
    
    def get_type(self, var: str) -> Type | None:
        local_type = self.locals.get(var)
        if not local_type:
            if isinstance(self.parent, SymTab):
                return self.parent.get_type(var)
            else:
                return None
        else:
            return local_type
    
    def get_op_type(self, var:str) -> FunType:
        local_type = self.locals.get(var)
        if not local_type:
            if isinstance(self.parent, SymTab):
                return self.parent.get_op_type(var)
            else:
                raise Exception(f'Could not find type for operator "{var}".')
            
        else:
            return local_type
    
    def get_function_type(self, name:str) -> FunType:
        local_type = self.locals.get(name)
        if not local_type:
            if isinstance(self.parent, SymTab):
                return self.parent.get_function_type(name)
            else:
                raise Exception(f'Could not find type for function "{name}".')
            
        else:
            return local_type
    
    def set_type(self, var:str, type:Type) -> bool:
        #for assignment only
        local_type = self.locals.get(var)
        if not local_type:
            if isinstance(self.parent, SymTab):
                return self.parent.set_type(var, type)
            else:
                return False
        else:
            self.locals[var] = type
            return True


def typecheck_lower(node: ast.Expression, tab:SymTab) -> Type:
    match node:
        case ast.Literal():
            if type(node.value) == int:
                return Int
            elif type(node.value) == bool:
                return Bool
            elif node.value is None:
                return Unit
            else:
                raise Exception(f'{node.location}: Unexpected type. Expected Bool, Int or Unit.')

        case ast.Identifier():
            tab_type = tab.get_type(node.name)
            if tab_type is None:
                raise Exception(f'{node.location}: Variable not defined.')
            else:
                return tab_type
        
        case ast.VarDec():
            name = node.name.name
            
            #if tab.locals.get(name) is not None:
            #    raise Exception(f'{node.location}: Variable has already been declared.')
            
            node_type = typecheck(node.value, tab)
            tab.locals[name] = node_type
            return node_type
        
        case ast.Block():
            child_tab = SymTab({}, tab)
            for exp in node.expressions:
                #check the expressions are ok
                typecheck(exp, child_tab)
            return typecheck(node.result, child_tab)
        
        case ast.FunctionNode():
            func_type = tab.get_function_type(node.function.name)
            if typecheck(node.arguments[0], tab) == func_type.parameters[0]:
                return func_type.result
            else:
                raise Exception(f'{node.location}: Function "{node.function}" not defined.')
            
        
        case ast.UnaryOp():
            element_type = typecheck(node.element, tab)
            if node.op == '-':
                if element_type == Int:
                    return Int
                else:
                    raise Exception(f'{node.location}: Incompatible type {element_type} with operator "-". Expected Int.')
            elif node.op == 'not':
                if element_type == Bool:
                    return Bool
                else:
                    raise Exception(f'{node.location}: Incompatible type {element_type} with operator "not". Expected Bool.')

        
        case ast.Assignment():
            t1 = typecheck(node.left, tab)
            t2 = typecheck(node.right, tab)

            if t1 != t2:
                raise Exception(f'{node.location}: Expected two of the same type, got different types: {t1}, {t2}')
            else:
                if isinstance(node.left, ast.Identifier):
                    type_updated = tab.set_type(node.left.name, t2)
                    if type_updated:
                        return t1
                    else:
                        raise Exception(f'{node.location}: "{node.left.name}" has not been declared.')
                return t1

        case ast.BinaryOp():
            t1 = typecheck(node.left, tab)
            t2 = typecheck(node.right, tab)
            
            if node.op in ['==','!=']:
                if t1 == t2:
                    return Bool
                else:
                    raise Exception(f'{node.location}: Expected two of the same types, got {t1} and {t2}.')
            
            op_type = tab.get_op_type(node.op)

            if t1 != op_type.parameters[0] or t2 != op_type.parameters[1]:
                raise Exception(f'{node.location}: Expected {op_type.parameters[0]} and {op_type.parameters[1]}.')
            else:
                return op_type.result

        case ast.IfThenElse():
            t1 = typecheck(node.condition, tab)
            if t1 is not Bool:
                raise Exception(f'{node.location}: Expected a bool as the if condition.')
            t2 = typecheck(node.then_branch, tab)
            if node.else_branch is not None:
                t3 = typecheck(node.else_branch, tab)
                if t2 != t3:
                    raise Exception(f'{node.location}: Expected two of the same type, got {t2} and {t3}.')
            return t2

        case ast.Loop():
            t1 = typecheck(node.while_exp, tab)
            if t1 != Bool:
                raise Exception(f'{node.while_exp.location}: Expected Bool, got {t1}.')
            return typecheck(node.do_exp, tab)
            
    
    raise Exception(f'{node.location}: Unexpected node.')

def typecheck(node: ast.Expression, tab: SymTab | None = None) -> Type:
    if tab is not None:
        global_tab = tab
    else:
        global_tab = SymTab(locals={
            '+': FunType([Int, Int],Int),
            '-': FunType([Int, Int],Int),
            '*': FunType([Int, Int],Int),
            '/': FunType([Int, Int],Int),
            '%': FunType([Int, Int],Int),
            '<': FunType([Int, Int],Bool),
            '>': FunType([Int, Int],Bool),
            '<=': FunType([Int, Int],Bool),
            '>=': FunType([Int, Int],Bool),
            'or': FunType([Bool, Bool],Bool),
            'and': FunType([Bool, Bool],Bool),
            'print_int': FunType([Int], Unit),
            'print_bool': FunType([Bool], Unit)
        })
    return typecheck_lower(node, global_tab)