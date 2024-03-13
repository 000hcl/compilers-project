from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.ast import BinaryOp, Identifier, Literal, IfThenElse, FunctionNode, UnaryOp, Block, VarDec, Loop, Assignment
from compiler.objs.location import Location, L
import unittest

class ParserTest(unittest.TestCase):

    def test_parse_simple_valid_expressions(self) -> None:
        simple_addition_subtraction = tokenize('a+b-c;')
        parenthesized_add_sub = tokenize('3+(5-1);')
        parenthesized_add_sub_2 = tokenize('(3+5)-1;')
        
        parsed_1 = parse(simple_addition_subtraction)
        parsed_2 = parse(parenthesized_add_sub)
        parsed_3 = parse(parenthesized_add_sub_2)
        
        assert(parsed_1==BinaryOp(location=L,left=BinaryOp(location=L,left=Identifier(location=L,name='a'), op='+', right=Identifier(location=L,name='b')), op='-', right=Identifier(location=L,name='c')))
        assert(parsed_2==BinaryOp(location=L,left=Literal(location=L,value=3), op='+', right=BinaryOp(location=L,left=Literal(location=L,value=5), op='-', right=Literal(location=L,value=1))))
        assert(parsed_3==BinaryOp(location=L,left=BinaryOp(location=L,left=Literal(location=L,value=3), op='+', right=Literal(location=L,value=5)), op='-', right=Literal(location=L,value=1)))
        

    def test_parse_multiplication_and_division(self) -> None:
        multiplication = tokenize('a*2;')
        division = tokenize('1+2/4;')
        division_parenthesized = tokenize('(1+2)/4;')
        
        parsed_1 = parse(multiplication)
        parsed_2 = parse(division)
        parsed_3 = parse(division_parenthesized)
        
        assert(parsed_1 == BinaryOp(location=L,left=Identifier(location=L,name='a'), op='*', right=Literal(location=L,value=2)))
        assert(parsed_2 == BinaryOp(location=L,left=Literal(location=L,value=1),op='+',right=BinaryOp(location=L,left=Literal(L,2),op='/',right=Literal(L,4))))
        assert(parsed_3 == BinaryOp(location=L,left=BinaryOp(location=L,left=Literal(location=L,value=1),op='+',right=Literal(location=L,value=2)), op='/',right=Literal(location=L,value=4)))

    def test_garbage_at_end_raises_excpetion(self) -> None:
        tokens = tokenize('a+b c;')
        
        with self.assertRaises(Exception):
            parse(tokens)
    
    def test_parse_erroneus_expressions(self) -> None:
        tokens = tokenize('1+ ')
        tokens_2 = tokenize('-')
        with self.assertRaises(Exception):
            parse(tokens)
            
        with self.assertRaises(Exception):
            parse(tokens_2)
    
    
    def test_simple_if_else_then_expressions(self) -> None:
        if_then_else = tokenize('if a then b else c;')
        if_then = tokenize('if a then b;')
        
        parsed_1 = parse(if_then_else)
        parsed_2 = parse(if_then)
        
        assert(parsed_1 == IfThenElse(location=L, condition=Identifier(location=L,name='a'),then_branch=Identifier(location=L,name='b'),else_branch=Identifier(location=L,name='c')))
        assert(parsed_2 == IfThenElse(location=L, condition=Identifier(location=L,name='a'),then_branch=Identifier(location=L,name='b'),else_branch=None))

    def test_complex_if_else_then_expressions(self) -> None:
        if_then_else = tokenize('if a then b+2 else x * y;')
        if_then = tokenize('if a then b+c;')
        
        parsed_1 = parse(if_then_else)
        parsed_2 = parse(if_then)
        
        assert(parsed_1 == IfThenElse(location=L, condition=Identifier(location=L,name='a'), then_branch=BinaryOp(location=L,left=Identifier(location=L,name='b'),op='+',right=Literal(L,2)), else_branch=BinaryOp(location=L,left=Identifier(location=L,name='x'),op='*',right=Identifier(location=L,name='y'))))
        assert(parsed_2 == IfThenElse(location=L, condition=Identifier(location=L,name='a'), then_branch=BinaryOp(location=L,left=Identifier(location=L,name='b'),op='+',right=Identifier(location=L,name='c')), else_branch=None))
    
    def test_if_allowed_as_part_of_other_expressions(self) -> None:
        expr = parse(tokenize('1 + if true then 2 else 3;'))
        assert(expr == BinaryOp(location=L,left=Literal(location=L,value=1), op='+', right=IfThenElse(location=L, condition=Literal(L,True), then_branch=Literal(location=L,value=2), else_branch=Literal(location=L,value=3))))
    
    def test_invalid_if_else_then_branchession_raises_exception(self) -> None:
        invalid_1 = tokenize('if true 3')
        invalid_2 = tokenize('if a then')
        
        with self.assertRaises(Exception):
            parse(invalid_1)
        
        with self.assertRaises(Exception):
            parse(invalid_2)
    
    def test_parse_simple_function_calls(self) -> None:
        expr = parse(tokenize('f(a,b);'))
        expr_2 = parse(tokenize('g(a,b,c);'))
        assert(expr == FunctionNode(location=L, function=Identifier(location=L,name='f'),arguments=[Identifier(location=L,name='a'),Identifier(location=L,name='b')]))
        assert(expr_2 == FunctionNode(location=L, function=Identifier(location=L,name='g'),arguments=[Identifier(location=L,name='a'),Identifier(location=L,name='b'),Identifier(location=L,name='c')]))
        
    def test_parse_complex_function_calls(self) -> None:
        expr = parse(tokenize('f(a+4,c*d);'))
        expr_2 = parse(tokenize('f(g(a));'))
        #expr_3 = parse(tokenize('a+f(4,2-b)')) check if this should be supported?
        
        assert(expr == FunctionNode(location=L, function=Identifier(location=L,name='f'),arguments=[BinaryOp(location=L,left=Identifier(location=L,name='a'), op='+', right=Literal(location=L,value=4)),BinaryOp(location=L,left=Identifier(location=L,name='c'), op='*', right=Identifier(location=L,name='d'))]))
        assert(expr_2 == FunctionNode(location=L, function=Identifier(location=L,name='f'),arguments=[FunctionNode(location=L, function=Identifier(location=L,name='g'),arguments=[Identifier(location=L,name='a')])]))
        #assert(expr_3 == BinaryOp(location=L,left=Identifier(location=L,name='a'),op='+',right=FunctionNode(location=L, function=Identifier(location=L,name='f'), arguments=[Literal(location=L,value=4), BinaryOp(location=L,left=Literal(location=L,value=2),op='-',right=Identifier(location=L,name='b'))])))
    
    def test_invalid_function_calls_raise_exceptions(self) -> None:
        invalid_1 = tokenize('f(c')
        invalid_2 = tokenize('63(g)')
        
        with self.assertRaises(Exception):
            parse(invalid_1)
        
        with self.assertRaises(Exception):
            parse(invalid_2)
    
    def test_remainder_operator(self) -> None:
        expr = parse(tokenize(r'a%b;'))
        expr_2 = parse(tokenize('2%5+a;'))
        
        assert(expr == BinaryOp(location=L,left=Identifier(L,'a'), op='%', right=Identifier(L,'b')))
        assert(expr_2 == BinaryOp(location=L,left=BinaryOp(location=L,left=Literal(L,2),op='%',right=Literal(L,5)),op='+',right=Identifier(L,'a')))
    
    def test_comparison_operators(self) -> None:
        expr = parse(tokenize('a+b == 2*3+1;'))
        expr_2 = parse(tokenize('a<b != 5;'))
        expr_3 = parse(tokenize('a>b>c;'))
        
        assert(expr == BinaryOp(location=L,left=BinaryOp(location=L,left=Identifier(L,'a'), op='+', right=Identifier(L,'b')), op='==', right=BinaryOp(location=L,left=BinaryOp(location=L,left=Literal(L,2), op='*', right=Literal(L,3)),op='+',right=Literal(L,1))))
        assert(expr_2 == BinaryOp(location=L,left=BinaryOp(L,Identifier(L,'a'),'<',Identifier(L,'b')), op='!=', right=Literal(L,5)))
        assert(expr_3 == BinaryOp(location=L,left=BinaryOp(location=L,left=Identifier(L,'a'),op='>',right=Identifier(L,'b')),op='>',right=Identifier(L,'c')))
        
    def test_and_or_operators(self) -> None:
        expr = parse(tokenize('x or y and c+b;'))
        
        assert(expr == BinaryOp(location=L,left=Identifier(L,'x'), op='or', right=BinaryOp(location=L,left=Identifier(L,'y'), op='and', right=BinaryOp(L,Identifier(L,'c'),'+',Identifier(L,'b')))))
    
    def test_unary_operators(self) -> None:
        expr_simple = parse(tokenize('not a;'))
        expr_chained = parse(tokenize('---5;'))
        
        assert(expr_simple == UnaryOp(L,'not', Identifier(L,'a')))
        assert(expr_chained == UnaryOp(L,'-',UnaryOp(L,'-',UnaryOp(L,'-',Literal(L,5)))))
        
    def test_assignment(self) -> None:
        expr = parse(tokenize('a=322;'))
        expr_2 = parse(tokenize('a=b=c;'))
        assert(expr == Assignment(location=L,left=Identifier(L,'a'), right=Literal(L,322)))
        assert(expr_2 == Assignment(location=L,left=Identifier(L,'a'),right=Assignment(L,Identifier(L,'b'),right=Identifier(L,'c'))))
    
    def test_erroneous_block_raises_exception(self) -> None:
        expr = tokenize(r'{ string;')
        
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
        assert(expr_simple == Assignment(location=L,left=Identifier(L,'x'),right=Block(location=L,expressions=[FunctionNode(location=L, function=Identifier(L,'f'),arguments=[Literal(L,5)])], result=Literal(location=L,value=322))))
        assert(expr_no_res == Assignment(location=L,left=Identifier(L,'x'),right=Block(location=L,expressions=[FunctionNode(location=L, function=Identifier(L,'f'),arguments=[Literal(L,5)]),Literal(location=L,value=322)], result=Literal(location=None,value=None))))
        assert(expr_block_in_block == Block(L,[IfThenElse(L,Literal(L,True), Block(L,[FunctionNode(L,Identifier(L,'f'),[Identifier(L,'x')])],Literal(None,None)),None),FunctionNode(L,Identifier(L,'g'),[Identifier(L,'x')])],Literal(None,None)))
    
    def test_invalid_var_declarations(self) -> None:
        invalid_1 = '{var 2 = 5}'
        invalid_2 = '{var = w}'
        invalid_3 = r'a = {x = y;var i = 5}'
        invalid_4 = 'if true then var i=4 else var i=5;'
        
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
        
        assert(expr == Block(L,[VarDec(L,Identifier(L,'i'),Literal(L,23))],Literal(None,None)))
        assert(expr_2 == Block(L,[VarDec(L,Identifier(L,'c'),BinaryOp(L,Literal(L,5),'+',FunctionNode(L,Identifier(L,'f'),[Identifier(L,'x')])))],Literal(None,None)))
    
    def test_invalid_blocks(self) -> None:
        invalid_1 = r'{a b}'
        invalid_2 = r'{if true then {a} b c}'
        
        with self.assertRaises(Exception):
            parse(tokenize(invalid_1))
        with self.assertRaises(Exception):
            parse(tokenize(invalid_2))
    
    def test_valid_blocks_optional_semicolon(self) -> None:
        expr_1 = parse(tokenize(r'{{a;}{b;}}'))
        expr_2 = parse(tokenize(r'{ if true then { a } b }'))
        expr_3 = parse(tokenize(r'{ if true then { a }; b }'))
        expr_4 = parse(tokenize(r'{ if true then { a } b; c }'))
        expr_5 = parse(tokenize(r'{ if true then { a } else { b } 3 }'))
        expr_6 = parse(tokenize(r'x = { { f(a) } { b } }'))
        
        assert(expr_1 == Block(L,[Block(L,[Identifier(L,'a')],Literal(None,None))], Block(L,[Identifier(L,'b')],Literal(None,None))))
        assert(expr_2 == Block(L,[IfThenElse(L,Literal(L,True),Block(L,[],Identifier(L,'a')),None)],Identifier(L,'b')))
        assert(expr_3 == Block(L,[IfThenElse(L,Literal(L,True),Block(L,[],Identifier(L,'a')),None)],Identifier(L,'b')))
        assert(expr_4 == Block(L,[IfThenElse(L,Literal(L,True),Block(L,[],Identifier(L,'a')),None),Identifier(L,'b')],Identifier(L,'c')))
        assert(expr_5 == Block(L,[IfThenElse(L,Literal(L,True),Block(L,[],Identifier(L,'a')),Block(L,[],Identifier(L,'b')))],Literal(L,3)))
        assert(expr_6 == Assignment(L,Identifier(L,'x'),Block(L,[Block(L,[],FunctionNode(L,Identifier(L,'f'),[Identifier(L,'a')]))],Block(L,[],Identifier(L,'b')))))
        
        
    def test_locations(self) -> None:
        expr = parse(tokenize('if true then {a+f(5);}'))
        
        assert(expr == IfThenElse(location=Location('Null', 0,0),condition=Literal(Location('Null', 0,3),True),then_branch=Block(Location('Null', 0,13),[BinaryOp(Location('Null', 0,14),Identifier(Location('Null', 0,14),'a'),'+',FunctionNode(Location('Null', 0,16),Identifier(Location('Null', 0,16),'f'),[Literal(Location('Null', 0,18),5)]))],Literal(None,None)), else_branch=None))
    
    def test_empty_blocks(self) -> None:
        expr = parse(tokenize(r'{}'))
        expr_2 = parse(tokenize(''))
        
        assert(expr == Block(L,[],Literal(None,None)))
        assert(expr_2 == Block(None,[],Literal(None,None)))
    
    def test_while_loop(self) -> None:
        expr = parse(tokenize(r'while true do {f(x);}'))
        
        assert(expr == Loop(L,Literal(L,True),Block(L,[FunctionNode(L,Identifier(L,'f'),[Identifier(L,'x')])],Literal(None,None))))
    
    def test_comments_ignored(self) -> None:
        expr = parse(tokenize("""
                              // comment
                              a;
                              # another comment
                              b;
                              """))
        
        assert(expr == Block(L,[Identifier(L,'a'),Identifier(L,'b')], Literal(None, None)))
    
    def test_top_level_expressions(self) -> None:
        expr = parse(tokenize(r"""
                              a;
                              {b}
                              """))
        
        assert(expr == Block(L,[Identifier(L,'a'),Block(L,[],Identifier(L,'b'))], Literal(None,None)))

    def test_invalid_top_level_expressions(self) -> None:
        invalid_1 = tokenize("""
                             a
                             b
                             """)
        #assumed that result expressions are not allowed in top level.
        invalid_2 = tokenize("""
                             a;
                             b
                             """)
        
        with self.assertRaises(Exception):
            parse(invalid_1)
        
        with self.assertRaises(Exception):
            parse(invalid_2)
    
    def test(self) -> None:
        #just to check that it parses at all
        parse(tokenize("""
                       {
                            while f() do {
                                x = 10;
                                y = if g(x) then {
                                    x = x + 1;
                                    x
                                } else {
                                    g(x)
                                };  # <-- (this semicolon will become optional later)
                                g(y);
                            };  # <------ (this too)
                            123
                        }


                       """))