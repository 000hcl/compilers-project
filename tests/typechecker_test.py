from compiler.ast import BinaryOp, Identifier, Literal, IfThenElse, FunctionNode, UnaryOp, Block, VarDec, Loop
from compiler.objs.types import Int, Bool, Type, FunType, Unit
from compiler.objs.location import Location, L
from compiler.typechecker import typecheck, SymTab
from compiler.parser import parse
from compiler.tokenizer import tokenize
import unittest

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

class TypeCheckerTest(unittest.TestCase):
    def test_check_type_literals(self) -> None:
        input = '3;'
        input_2 = 'true;'
        
        assert(typecheck(parse(tokenize(input))) == Int)
        assert(typecheck(parse(tokenize(input_2))) == Bool)
    
    def test_check_type_variables(self) -> None:
        tab = SymTab({'x': Int, 'y':Bool}, None)
        input = 'x;'
        input_2 = 'y;'
        
        assert(typecheck(parse(tokenize(input)),tab)==Int)
        assert(typecheck(parse(tokenize(input_2)),tab)==Bool)
    
    def test_untyped_var_declaration_type(self) -> None:
        input = 'var x = 23;'

        tab = SymTab({'x': Int},global_tab)
        input_2 = 'var y = 2+x;'
        
        assert(typecheck(parse(tokenize(input))) == Int)
        assert(typecheck(parse(tokenize(input_2)),tab) == Int)
    
    def test_literal_none_type_is_unit(self) -> None:
        assert(typecheck(Literal(L,None)) == Unit)
    
    def test_assignment(self) -> None:
        input = parse(tokenize('x=10;'))
        parent_tab = SymTab({'y': Bool, 'z':Int},None)
        tab = SymTab({'x':Int}, parent_tab)
        with self.assertRaises(Exception):
            typecheck(input)
        
        with self.assertRaises(Exception):
            typecheck(parse(tokenize('y=23;')), tab)
        
        result_1 = typecheck(input, tab)
        assert(result_1 == Int)
        
        result_2 = typecheck(parse(tokenize('y=true;')), tab)
        assert(result_2 == Bool)
        
        result_3 = typecheck(parse(tokenize('x=z=45;')), tab)
        assert(result_3 == Int)
    
    def test_unary_type_check(self) -> None:
        invalid_1 = parse(tokenize('not 45;'))
        invalid_2 = parse(tokenize('--true;'))
        
        with self.assertRaises(Exception):
            typecheck(invalid_1)
        with self.assertRaises(Exception):
            typecheck(invalid_2)
        
        valid_1 = typecheck(parse(tokenize('--45;')))
        valid_2 = typecheck(parse(tokenize('not true;')))
        
        assert(valid_1 == Int)
        assert(valid_2 == Bool)
    
    def test_binary_operators(self) -> None:
        i1 = typecheck(parse(tokenize('1-2;')))
        i2 = typecheck(parse(tokenize('23>1;')))
        i3 = typecheck(parse(tokenize('true and 2<4;')))
        i4 = typecheck(parse(tokenize('1 == 3;')))
        invalid = parse(tokenize('true - 4;'))
        invalid_2 = parse(tokenize('21 != true;'))
        
        assert(i1 == Int)
        assert(i2 == Bool)
        assert(i3 == Bool)
        assert(i4 == Bool)
        with self.assertRaises(Exception):
            typecheck(invalid)
        with self.assertRaises(Exception):
            typecheck(invalid_2)
    
    def test_base_functions_type_check(self) -> None:
        i1 = typecheck(parse(tokenize('print_int(23);')))
        i2 = typecheck(parse(tokenize('print_bool(1>2);')))
        
        assert(i1==Unit)
        assert(i2==Unit)
    
    def test_blocks(self) -> None:
        i1 = typecheck(parse(tokenize(r'{}')))
        i2 = typecheck(parse(tokenize(r'{var x = 3; x = 5; 23}')))
        i3 = typecheck(parse(tokenize(r'{var x = 3; x = 5;}')))
        
        invalid = parse(tokenize(r'{x = 5; 23}'))
        
        assert(i1==Unit)
        assert(i2 == Int)
        assert(i3==Unit)
        with self.assertRaises(Exception):
            typecheck(invalid)
    
    def test_if_else_then(self) -> None:
        i1 = typecheck(parse(tokenize('if true then 2 else 4;')))
        i2 = typecheck(parse(tokenize('1 + if 1>2 then 3 else 34;')))
        i3 = typecheck(parse(tokenize('if true then 3;')))
        invalid = parse(tokenize('if true then 3 else false;'))
        invalid_2 = parse(tokenize('if 4 then false;'))
        
        assert(i1 == Int)
        assert(i2==Int)
        assert(i3 == Int)
        with self.assertRaises(Exception):
            typecheck(invalid)
        with self.assertRaises(Exception):
            typecheck(invalid_2)
    
    def test_while_loop(self) -> None:
        valid = typecheck(parse(tokenize(r'while true do {print_int(23);}')))
        #TODO: check if valid:
        valid_2 = typecheck(parse(tokenize(r'while true do {print_int(23);45}')))
        invalid = parse(tokenize(r'while 23 do {print_int(23);}'))

        with self.assertRaises(Exception):
            typecheck(invalid)
        
        assert(valid == Unit)
        assert(valid_2 == Int)
        