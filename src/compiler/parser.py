#from compiler.tokenizer import Token
from compiler.objs.tokenclass import Token
#from compiler.objs.location import Location
import compiler.ast as ast

def parse(tokens: list[Token]) -> ast.Expression:
    left_associative_binary_operators = [
        ['or'],
        ['and'],
        ['==', '!='],
        ['<', '<=', '>', '>='],
        ['+','-'],
        ['*', '/', '%']
    ]
    
    precedence_levels_binary_op = len(left_associative_binary_operators)
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
    
    def parse_bool_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f'{peek().loc}: expected a boolean literal')
        token = consume()
        return ast.Literal(bool(token.text))

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
    
    def parse_assignment(left: ast.Expression) -> ast.Expression:
        
        if peek().text == '=':
            consume('=')
            right = parse_assignment(parse_expression())
        else:
            return left
        
        return ast.BinaryOp(left=left, op='=', right=right)

    
    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == '{':
            return parse_block()
        elif peek().text in ['-', 'not']:
            return parse_unary()
        elif peek().text == 'if':
            return parse_control()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'bool_literal':
            return parse_bool_literal()
        elif peek().type == 'identifier':
            return parse_identifier()
        else:
            raise Exception(f'{peek().loc}: expected an integer literal or an identifier. Got {peek().type}.')
    
    def parse_unary() -> ast.Expression:
        operator = peek().text
        consume(['-','not'])
        element = parse_expression()
        return ast.UnaryOp(op=operator, element=element)

    
    def parse_function_call(function: ast.Expression) -> ast.Expression:
        consume('(')
        arguments = [parse_expression()]
        while peek().text == ',':
            consume(',')
            arguments.append(parse_expression())
        consume(')')
        return ast.FunctionNode(function=function, arguments=arguments)

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
    
    def parse_var_declaration() -> ast.Expression:
        #assumed var x = y = z not allowed.
        consume('var')
        name = parse_identifier()
        print('NAME',name)
        consume('=')
        value = parse_expression()
        
        return ast.VarDec(name=name, value=value)
        
    
    def parse_expression(level: int = 0) -> ast.Expression:
        nonlocal precedence_levels_binary_op
        nonlocal left_associative_binary_operators
        
        if level >= precedence_levels_binary_op:
            return parse_factor()
        else:
            left = parse_expression(level+1)
        
        if peek().text == '(':
            left = parse_function_call(left)
        
        #if assignment:
        if peek().text == '=':
            return parse_assignment(left)
        
        while peek().text in left_associative_binary_operators[level]:
            operator_token = consume()
            operator = operator_token.text
            
            right = parse_expression(level+1)
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
    
        
        
        return left
    
    def parse_block() -> ast.Expression:
        expressions = []
        consume('{')
        if peek().text == 'var':
            expr = parse_var_declaration()
        else:
            expr = parse_expression()
        while peek().text == ';':
            expressions.append(expr)
            consume(';')
            if peek().text == '}':
                expr = ast.Literal(value=None)
            else:
                if peek().text == 'var':
                    expr = parse_var_declaration()
                else:
                    expr = parse_expression()

        #result should not be var declaration?
        if isinstance(expr, ast.VarDec):
            raise Exception(f'Result should not be a variable declaration.')
        consume('}')
        return ast.Block(expressions=expressions, result=expr)
            
    
    def parse_and_handle_entire_expression() -> ast.Expression:
        expr = parse_expression()
        #if leftover tokens, raise excpetion
        if peek().type != 'end':
            raise Exception(f'{peek().loc}: Unexpected token. Could not parse: {peek().type} "{peek().text}".')
        return expr
    
    return parse_and_handle_entire_expression()

