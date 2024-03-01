import re
from compiler.objs.tokenclass import Token
from compiler.objs.location import Location, L
#from objs.tokenclass import Token
#from objs.location import Location, L




def tokenize(source_code: str) -> list[Token]:
    token_r = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]+|[a-zA-Z]')
    wr = re.compile(r'[\n ]+')
    wr_nl = re.compile(r'[\n ]*\n')
    int_lit_r = re.compile(r'[0-9]+')
    operator_r = re.compile(r'==|!=|<=|>=|[+-=*/%]')
    comment_r = re.compile(r'(#|//).*\n')
    punctuation_r = re.compile(r'[(){},;]')
    length = len(source_code)
    i = 0
    tokens = []
    line = 0
    last_newline_i = 0
    while i < length:
        start = i
        whitespace_result = wr.match(source_code,i)
        whitespace_until_nl = wr_nl.match(source_code,i)
        token_result = token_r.match(source_code, i)
        int_lit_result = int_lit_r.match(source_code, i)
        operator_result = operator_r.match(source_code, i)
        comment_result = comment_r.match(source_code, i)
        punctuation_result = punctuation_r.match(source_code, i)
        
        token_type = None
        
        if comment_result:
            #ignore comment
            line += 1
            last_newline_i = comment_result.end()
            i = comment_result.end()
        
        elif whitespace_result:
            newlines = whitespace_result.group().count('\n')
            if whitespace_until_nl:
                last_newline_i = whitespace_until_nl.end()
            line += newlines
            i = whitespace_result.end()
        
        elif punctuation_result:
            token_text = punctuation_result.group()
            token_type = 'punctuation'
            i = punctuation_result.end()

        elif token_result:
            token_text = token_result.group()
            token_type = 'identifier'
            i = token_result.end()
        elif int_lit_result:
            token_text = int_lit_result.group()
            token_type = 'int_literal'
            i = int_lit_result.end()
        elif operator_result:
            token_text = operator_result.group()
            token_type = 'operator'
            i = operator_result.end()
        else:
            i += 1
        
        if token_type:
            loc_col = start-last_newline_i
            location = Location(row=line, column=loc_col)
            token = Token(token_text, token_type, location)
            tokens.append(token)

    return tokens


#t = """def function
#        return 20
#    string
#    def functionfor i in range(len(tks)):
#    print(tks[i],expected[i])
#        print 23
#        return 23"""
#tks = tokenize(test_input)

