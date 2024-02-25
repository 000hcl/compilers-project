#from compiler.tokenizer import Token
from compiler.objs.tokenclass import Token
#from compiler.objs.location import Location
import compiler.ast as ast

def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0
    
    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            if len(tokens) == 0:
                location = None
            else:
                location = tokens[-1].loc
            return Token(
                loc= location,
                type='end',
                text=''
            )
    
    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.loc}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.loc}: expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token
    
    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f'{peek().loc}: expected an integer literal')
        token = consume()
        return ast.Literal(int(token.text))
    
    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().loc}: expected an identifier')
        token = consume()
        return ast.Identifier(token.text)
    
    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        if peek().text == 'if':
            return parse_control()
        if peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'identifier':
            return parse_identifier()
        else:
            raise Exception(f'{peek().loc}: expected an integer literal or an identifier')

    def parse_term() -> ast.Expression:
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    def parse_expression() -> ast.Expression:
        #print(pos)
        left = parse_term()
        
        while peek().text in ['+','-']:
            print(pos)
            operator_token = consume()
            operator = operator_token.text
            
            right = parse_term()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        
        
        
        return left
    
    #TODO: testing, update to new version
    """
    def parse_expression_right() -> ast.BinaryOp:
        pos_copy = pos
        #get all relevant tokens
        expression_tokens = [consume()]
        while peek().text in ['+','-']:
            #consume operator
            expression_tokens.append(consume())
            #consume right integer
            expression_tokens.append(consume())
            
        
        #reverse list
        expression_tokens = expression_tokens[::-1]
        #parse
        right = parse_term(expression_tokens[0])
        for tkn in expression_tokens[1:]:
            if tkn.text in ['+','-']:
                op_token = tkn.text
            else:
                left = parse_term(tkn)
                right = ast.BinaryOp(
                    left,
                    op_token,
                    right
                )
        return right
    """
    def parse_control() -> ast.Expression:
        consume('if')
        if_expr = parse_expression()
        consume('then')
        then_expr = parse_expression()
        else_expr = None
        if peek().text == 'else':
            consume('else')
            else_expr = parse_expression()
        return ast.ControlNode(if_expr, then_expr, else_expr)

    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr
    
    def parse_and_handle_entire_expression() -> ast.Expression:
        expr = parse_expression()
        #if leftover tokens, raise excpetion
        if peek().type != 'end':
            raise Exception(f'{peek().loc}: Unexpected token. Could not parse: {peek().type} "{peek().text}".')
        return expr
    
    return parse_and_handle_entire_expression()

