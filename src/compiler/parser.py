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
    
    def lookback() -> Token:
        if pos > 0:
            return tokens[pos-1]
        else:
            return Token(
                loc = None,
                type='start',
                text=''
            )
    
    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token.loc}: expected "{expected}", got {token.text}')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.loc}: expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token
    
    def parse_bool_literal() -> ast.Literal:
        if peek().type != 'bool_literal':
            raise Exception(f'{peek().loc}: expected a boolean literal')
        token = consume()
        if token.text == 'true':
            value = True
        elif token.text == 'false':
            value = False
        else:
            raise Exception(f'{token.loc}: Expected "true" or "false", got {token.text}.')
        return ast.Literal(value=value, location=token.loc)

    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f'{peek().loc}: expected an integer literal')
        token = consume()
        return ast.Literal(value=int(token.text), location=token.loc)
    
    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().loc}: expected an identifier')
        token = consume()
        return ast.Identifier(name=token.text, location=token.loc)
    
    def parse_assignment(left: ast.Expression) -> ast.Expression:
        
        if peek().text == '=':
            consume('=')
            right = parse_assignment(parse_expression())
        else:
            return left
        return ast.Assignment(location=left.location, left=left, right=right)
        #return ast.BinaryOp(left=left, op='=', right=right, location=left.location)

    
    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == '{':
            return parse_block()
        elif peek().text in ['-', 'not']:
            return parse_unary()
        elif peek().text == 'if':
            return parse_control()
        elif peek().text == 'while':
            return parse_loop()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'bool_literal':
            return parse_bool_literal()
        elif peek().type == 'identifier':
            return parse_identifier()
        else:
            raise Exception(f'{peek().loc}: expected an integer literal or an identifier. Got {peek().type} "{peek().text}".')
    
    def parse_unary() -> ast.Expression:
        operator = peek().text
        not_token = consume(['-','not'])
        element = parse_expression()
        return ast.UnaryOp(op=operator, element=element, location=not_token.loc)

    def parse_function_call(function: ast.Identifier) -> ast.Expression:
        consume('(')
        arguments = []
        if peek().text != ')':
            arguments.append(parse_expression())
        while peek().text == ',':
            consume(',')
            arguments.append(parse_expression())
        consume(')')
        return ast.FunctionNode(function=function, arguments=arguments, location=function.location)

    def parse_control() -> ast.Expression:
        start_token = consume('if')
        conditionr = parse_expression()
        consume('then')
        then_branch = parse_expression()
        else_branch = None
        if peek().text == 'else':
            consume('else')
            else_branch = parse_expression()
        return ast.IfThenElse(condition=conditionr, then_branch=then_branch, else_branch=else_branch, location=start_token.loc)

    def parse_parenthesized() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr
    
    def parse_var_declaration() -> ast.Expression:
        #assumed var x = y = z not allowed.
        start_token = consume('var')
        name = parse_identifier()
        var_type = None
        if peek().text != '=':
            consume(':')
            var_type = parse_type_expression(name)
        consume('=')
        value = parse_expression()
        
        
        return ast.VarDec(name=name, value=value, location=start_token.loc, dec_type=var_type)
    
    def parse_type_expression(var: ast.Identifier) -> ast.TypeExpr:
        if peek().text in ['Int','Bool','Unit']:
            token = consume()
            return ast.SimpleType(var, token.loc ,token.text)
        elif peek().text == '(':
            params = []
            first = consume('(')
            params.append(parse_type_expression(var))
            while peek().text == ',':
                consume(',')
                params.append(parse_type_expression(var))
            consume(')')
            consume('=')
            consume('>')
            
            result = parse_type_expression(var)
            return ast.TypeFunction(var, first.loc, params, result)
        else:
            raise Exception(f'{peek().loc}: Could not parse type "{peek().text}".')

        
    
    def parse_loop() -> ast.Expression:
        start_token = consume('while')
        while_exp = parse_expression()
        consume('do')
        do_exp = parse_expression()
        
        return ast.Loop(location=start_token.loc, while_exp=while_exp,do_exp=do_exp)
        
    
    def parse_expression(level: int = 0) -> ast.Expression:
        nonlocal precedence_levels_binary_op
        nonlocal left_associative_binary_operators
        
        if level >= precedence_levels_binary_op:
            return parse_factor()
        else:
            left = parse_expression(level+1)
        
        if peek().text == '(' and isinstance(left, ast.Identifier):
            left = parse_function_call(left)
        
        #if assignment:
        if peek().text == '=':
            return parse_assignment(left)
        
        while peek().text in left_associative_binary_operators[level]:
            operator_token = consume()
            operator = operator_token.text
            
            right = parse_expression(level+1)
            left = ast.BinaryOp(
                left=left,
                op=operator,
                right=right,
                location=left.location
            )

        return left
    
    def parse_block() -> ast.Expression:
        expressions: list[ast.Expression] = []
        start_token = consume('{')
        if peek().text == 'var':
            expr = parse_var_declaration()
        elif peek().text != '}':
            expr = parse_expression()
        else:
            expr = ast.Literal(value=None, location=None)

        while (peek().text == ';' or (lookback().text == '}' and (peek().text not in [';','}']))):

            expressions.append(expr)
            if peek().text == ';':
                consume(';')
            if peek().text == '}':
                expr = ast.Literal(value=None, location=None)
            else:
                if peek().text == 'var':
                    expr = parse_var_declaration()
                else:
                    expr = parse_expression()

        #result should not be var declaration?
        if isinstance(expr, ast.VarDec):
            raise Exception(f'{expr.location}: Result should not be a variable declaration.')
        consume('}')
        return ast.Block(expressions=expressions, result=expr, location=start_token.loc)
            
    
    def parse_top_level() -> ast.Expression:
        expressions: list[ast.Expression] = []
        while True:
            if peek().type == 'end':
                break
            if lookback().text not in [';','}'] and lookback().type!='start' and peek().type != 'end':
                break
            if peek().text == 'var':
                expr = parse_var_declaration()
            else:
                expr = parse_expression()
            if lookback().text != '}':
                consume(';')
            expressions.append(expr)

        if len(expressions)>0:
            start = expressions[0].location
        else:
            start = None
        
        if len(expressions) == 1:
            return expressions[0]
        else:
            return ast.Block(expressions=expressions, result=ast.Literal(None,None), location=start)
    
    def parse_and_handle_entire_expression() -> ast.Expression:
        expr = parse_top_level()
        #if leftover tokens, raise excpetion
        if peek().type != 'end':
            raise Exception(f'{peek().loc}: Unexpected token. Could not parse: {peek().type} "{peek().text}".')
        return expr
    
    return parse_and_handle_entire_expression()

