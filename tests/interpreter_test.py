from compiler.ast import BinaryOp, Identifier, Literal, IfThenElse, FunctionNode, UnaryOp, Block, VarDec, Loop
from compiler.objs.location import Location, L
from compiler.interpreter import interpret
from compiler.parser import parse
from compiler.tokenizer import tokenize
import unittest



class InterpreterTest(unittest.TestCase):
    def test_interpret_basic_operators(self) -> None:
        result = interpret(parse(tokenize('2+3;')))
    
        assert(result == 5)