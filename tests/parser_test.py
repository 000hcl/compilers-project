from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import BinaryOp, Identifier, Literal, ControlNode, FunctionNode, UnaryOp, Block, VarDec
import unittest

class ParserTest(unittest.TestCase):

    def test_parse_simple_valid_expressions(self) -> None:
        simple_addition_subtraction = tokenize('a+b-c')
        parenthesized_add_sub = tokenize('3+(5-1)')
        parenthesized_add_sub_2 = tokenize('(3+5)-1')
        
        parsed_1 = parse(simple_addition_subtraction)
        parsed_2 = parse(parenthesized_add_sub)
        parsed_3 = parse(parenthesized_add_sub_2)
        
        assert(parsed_1==BinaryOp(left=BinaryOp(left=Identifier(name='a'), op='+', right=Identifier(name='b')), op='-', right=Identifier(name='c')))
        assert(parsed_2==BinaryOp(left=Literal(value=3), op='+', right=BinaryOp(left=Literal(value=5), op='-', right=Literal(value=1))))
        assert(parsed_3==BinaryOp(left=BinaryOp(left=Literal(value=3), op='+', right=Literal(value=5)), op='-', right=Literal(value=1)))
        

    def test_parse_multiplication_and_division(self) -> None:
        multiplication = tokenize('a*2')
        division = tokenize('1+2/4')
        division_parenthesized = tokenize('(1+2)/4')
        
        parsed_1 = parse(multiplication)
        parsed_2 = parse(division)
        parsed_3 = parse(division_parenthesized)
        
        assert(parsed_1 == BinaryOp(left=Identifier(name='a'), op='*', right=Literal(value=2)))
        assert(parsed_2 == BinaryOp(left=Literal(value=1),op='+',right=BinaryOp(left=Literal(2),op='/',right=Literal(4))))
        assert(parsed_3 == BinaryOp(left=BinaryOp(left=Literal(value=1),op='+',right=Literal(value=2)), op='/',right=Literal(value=4)))

    def test_garbage_at_end_raises_excpetion(self) -> None:
        tokens = tokenize('a+b c')
        
        with self.assertRaises(Exception):
            parse(tokens)
    
    def test_parse_erroneus_expressions(self) -> None:
        tokens = tokenize('1+ ')
        tokens_2 = tokenize('-')
        with self.assertRaises(Exception):
            parse(tokens)
            
        with self.assertRaises(Exception):
            parse(tokens_2)
    
    def test_empty_input_parsed(self) -> None:
        with self.assertRaises(Exception):
            parse([])
    
    def test_simple_if_else_then_expressions(self) -> None:
        if_then_else = tokenize('if a then b else c')
        if_then = tokenize('if a then b')
        
        parsed_1 = parse(if_then_else)
        parsed_2 = parse(if_then)
        
        assert(parsed_1 == ControlNode(if_exp=Identifier(name='a'),then_exp=Identifier(name='b'),else_exp=Identifier(name='c')))
        assert(parsed_2 == ControlNode(if_exp=Identifier(name='a'),then_exp=Identifier(name='b'),else_exp=None))

    def test_complex_if_else_then_expressions(self) -> None:
        if_then_else = tokenize('if a then b+2 else x * y')
        if_then = tokenize('if a then b+c')
        
        parsed_1 = parse(if_then_else)
        parsed_2 = parse(if_then)
        
        assert(parsed_1 == ControlNode(if_exp=Identifier(name='a'), then_exp=BinaryOp(left=Identifier(name='b'),op='+',right=Literal(2)), else_exp=BinaryOp(left=Identifier(name='x'),op='*',right=Identifier(name='y'))))
        assert(parsed_2 == ControlNode(if_exp=Identifier(name='a'), then_exp=BinaryOp(left=Identifier(name='b'),op='+',right=Identifier(name='c')), else_exp=None))
    
    def test_if_allowed_as_part_of_other_expressions(self) -> None:
        expr = parse(tokenize('1 + if true then 2 else 3'))
        assert(expr == BinaryOp(left=Literal(value=1), op='+', right=ControlNode(if_exp=Identifier(name='true'), then_exp=Literal(value=2), else_exp=Literal(value=3))))
    
    def test_invalid_if_else_then_expression_raises_exception(self) -> None:
        invalid_1 = tokenize('if true 3')
        invalid_2 = tokenize('if a then')
        
        with self.assertRaises(Exception):
            parse(invalid_1)
        
        with self.assertRaises(Exception):
            parse(invalid_2)
    
    def test_parse_simple_function_calls(self) -> None:
        expr = parse(tokenize('f(a,b)'))
        expr_2 = parse(tokenize('g(a,b,c)'))
        assert(expr == FunctionNode(function=Identifier(name='f'),arguments=[Identifier(name='a'),Identifier(name='b')]))
        assert(expr_2 == FunctionNode(function=Identifier(name='g'),arguments=[Identifier(name='a'),Identifier(name='b'),Identifier(name='c')]))
        
    def test_parse_complex_function_calls(self) -> None:
        expr = parse(tokenize('f(a+4,c*d)'))
        expr_2 = parse(tokenize('f(g(a))'))
        #expr_3 = parse(tokenize('a+f(4,2-b)')) check if this should be supported?
        
        assert(expr == FunctionNode(function=Identifier(name='f'),arguments=[BinaryOp(left=Identifier(name='a'), op='+', right=Literal(value=4)),BinaryOp(left=Identifier(name='c'), op='*', right=Identifier(name='d'))]))
        assert(expr_2 == FunctionNode(function=Identifier(name='f'),arguments=[FunctionNode(function=Identifier(name='g'),arguments=[Identifier(name='a')])]))
        #assert(expr_3 == BinaryOp(left=Identifier(name='a'),op='+',right=FunctionNode(function=Identifier(name='f'), arguments=[Literal(value=4), BinaryOp(left=Literal(value=2),op='-',right=Identifier(name='b'))])))
    
    def test_invalid_function_calls_raise_exceptions(self) -> None:
        invalid_1 = tokenize('f(c')
        invalid_2 = tokenize('g)')
        
        with self.assertRaises(Exception):
            parse(invalid_1)
        
        with self.assertRaises(Exception):
            parse(invalid_2)
    
    def test_remainder_operator(self) -> None:
        expr = parse(tokenize(r'a%b'))
        expr_2 = parse(tokenize('2%5+a'))
        
        assert(expr == BinaryOp(left=Identifier('a'), op='%', right=Identifier('b')))
        assert(expr_2 == BinaryOp(left=BinaryOp(left=Literal(2),op='%',right=Literal(5)),op='+',right=Identifier('a')))
    
    def test_comparison_operators(self) -> None:
        expr = parse(tokenize('a+b == 2*3+1'))
        expr_2 = parse(tokenize('a<b != 5'))
        expr_3 = parse(tokenize('a>b>c'))
        
        assert(expr == BinaryOp(left=BinaryOp(left=Identifier('a'), op='+', right=Identifier('b')), op='==', right=BinaryOp(left=BinaryOp(left=Literal(2), op='*', right=Literal(3)),op='+',right=Literal(1))))
        assert(expr_2 == BinaryOp(left=BinaryOp(Identifier('a'),'<',Identifier('b')), op='!=', right=Literal(5)))
        assert(expr_3 == BinaryOp(left=BinaryOp(left=Identifier('a'),op='>',right=Identifier('b')),op='>',right=Identifier('c')))
        
    def test_and_or_operators(self) -> None:
        expr = parse(tokenize('x or y and c+b'))
        
        assert(expr == BinaryOp(left=Identifier('x'), op='or', right=BinaryOp(left=Identifier('y'), op='and', right=BinaryOp(Identifier('c'),'+',Identifier('b')))))
    
    def test_unary_operators(self) -> None:
        expr_simple = parse(tokenize('not a'))
        expr_chained = parse(tokenize('---5'))
        
        assert(expr_simple == UnaryOp('not', Identifier('a')))
        assert(expr_chained == UnaryOp('-',UnaryOp('-',UnaryOp('-',Literal(5)))))
        
    def test_assignment(self) -> None:
        expr = parse(tokenize('a=322'))
        expr_2 = parse(tokenize('a=b=c'))
        assert(expr == BinaryOp(left=Identifier('a'), op='=', right=Literal(322)))
        assert(expr_2 == BinaryOp(left=Identifier('a'),op='=',right=BinaryOp(Identifier('b'),op='=',right=Identifier('c'))))
    
    def test_empty_block_raises_exception(self) -> None:
        expr = tokenize(r'{ string')
        
        with self.assertRaises(Exception):
            parse(expr)
    
    def test_valid_blocks(self) -> None:
        expr_simple = parse(tokenize(r"""
                                     x = {
                                         f(5);
                                         322
                                     }
                                     """))
        expr_no_res = parse(tokenize(r"""
                                     x = {
                                         f(5);
                                         322;
                                     }
                                     """))
        expr_block_in_block = parse(tokenize(r"""
                                             {
                                                 if true then {
                                                     f(x);
                                                 };
                                                 g(x);
                                             }
                                             """))
        assert(expr_simple == BinaryOp(left=Identifier('x'),op='=',right=Block(expressions=[FunctionNode(function=Identifier('f'),arguments=[Literal(5)])], result=Literal(value=322))))
        assert(expr_no_res == BinaryOp(left=Identifier('x'),op='=',right=Block(expressions=[FunctionNode(function=Identifier('f'),arguments=[Literal(5)]),Literal(value=322)], result=Literal(value=None))))
        assert(expr_block_in_block == Block([ControlNode(Identifier('true'), Block([FunctionNode(Identifier('f'),[Identifier('x')])],Literal(None)),None),FunctionNode(Identifier('g'),[Identifier('x')])],Literal(None)))
    
    def test_invalid_var_declarations(self) -> None:
        invalid_1 = '{var 2 = 5}'
        invalid_2 = '{var = w}'
        invalid_3 = r'a = {x = y;var i = 5}'
        invalid_4 = 'if true then var i=4 else var i=5'
        
        with self.assertRaises(Exception):
            parse(tokenize(invalid_1))
        with self.assertRaises(Exception):
            parse(tokenize(invalid_2))
        with self.assertRaises(Exception):
            parse(tokenize(invalid_3))
        with self.assertRaises(Exception):
            parse(tokenize(invalid_4))
    
    def test_valid_var_declarations(self) -> None:
        expr = parse(tokenize(r'{var i=23;}'))
        expr_2 = parse(tokenize(r'{var c = 5+f(x);}'))
        #TODO: Top level expressions?
        
        assert(expr == Block([VarDec(Identifier('i'),Literal(23))],Literal(None)))
        assert(expr_2 == Block([VarDec(Identifier('c'),BinaryOp(Literal(5),'+',FunctionNode(Identifier('f'),[Identifier('x')])))],Literal(None)))
    
    def test_invalid_blocks(self) -> None:
        invalid_1 = r'{a b}'
        invalid_2 = r'{if true then {a} b c}'
        
        with self.assertRaises(Exception):
            parse(tokenize(invalid_1))
        with self.assertRaises(Exception):
            parse(tokenize(invalid_2))