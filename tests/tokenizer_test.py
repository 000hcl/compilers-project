from compiler.tokenizer import tokenize # type: ignore
from compiler.objs.tokenclass import Token
from compiler.objs.location import L, Location

#Task 1 tests

def test_tokenizer_basics() -> None:
    assert tokenize("if  3\nwhile") == [Token('if', 'identifier', L),
                                        Token('3', 'int_literal', L),
                                        Token('while', 'identifier', L)]


def test_tokenizer_whitespace_ignored() -> None:
    test_input = """
    def function
        return 20
    
    def function
        print 23
        return 23
    """
    
    expected = [Token('def', 'identifier', L),
                Token('function', 'identifier', L),
                Token('return', 'identifier', L),
                Token('20', 'int_literal', L),
                Token('def', 'identifier', L),
                Token('function', 'identifier', L),
                Token('print', 'identifier', L),
                Token('23', 'int_literal', L),
                Token('return', 'identifier', L),
                Token('23', 'int_literal', L)]
    assert tokenize(test_input) == expected
    
def test_tokenizer_valid_identifiers_and_literals() -> None:
    test_input = """
    def function _CommonObject
        int 1243
        string string_A
        string string_A2
        object Object_QW_89
    """
    
    expected = [Token('def', 'identifier', L),
                Token('function', 'identifier', L),
                Token('_CommonObject', 'identifier', L),
                Token('int', 'identifier', L),
                Token('1243', 'int_literal', L),
                Token('string', 'identifier', L),
                Token('string_A', 'identifier', L),
                Token('string', 'identifier', L),
                Token('string_A2', 'identifier', L),
                Token('object', 'identifier', L),
                Token('Object_QW_89', 'identifier', L)]
    assert tokenize(test_input) == expected

def test_operators_recognized() -> None:
    test_input = """
    1 == 2
    b = 3
    1<3
    """
    
    expected = [Token('1', 'int_literal', L),
                Token('==', 'operator', L),
                Token('2', 'int_literal', L),
                Token('b', 'identifier', L),
                Token('=', 'operator', L),
                Token('3', 'int_literal', L),
                Token('1', 'int_literal', L),
                Token('<', 'operator', L),
                Token('3', 'int_literal', L)]
    
    assert tokenize(test_input) == expected

def test_one_line_comments_skipped() -> None:
    test_input = """
    // comment
    a = 1
    # comment
    """
    
    expected = [
        Token('a', 'identifier', L),
        Token('=', 'operator', L),
        Token('1', 'int_literal', L)
    ]
    
    assert tokenize(test_input) == expected

def test_location_accurate_with_comments_and_whitespace() -> None:
    test_input = """"// long comment
    int 2
    
    # other comment
        string c
    """
    
    expected = [
        Token('int', 'identifier', Location(row=1,column=4)),
        Token('2', 'int_literal', Location(row=1, column=8)),
        Token('string', 'identifier', Location(row=4,column=8)),
        Token('c', 'identifier', Location(row=4,column=15))
    ]
    
    assert tokenize(test_input) == expected

def test_puncuation_recognized() -> None:
    test_input = r"""
    ;,(){}
    """
    expected = [
        Token(';', 'punctuation', L),
        Token(',', 'punctuation', L),
        Token('(', 'punctuation', L),
        Token(')', 'punctuation', L),
        Token('{', 'punctuation', L),
        Token('}', 'punctuation', L)
    ]
    
    assert tokenize(test_input) == expected