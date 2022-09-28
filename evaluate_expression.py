import logging
import string
from logging.config import IDENTIFIER

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('LANGUAGE')


PLUS = 'PLUS'
MINUS = 'MINUS'
MULTIPLY = 'MUL'
DIVIDE = 'DIV'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
INTEGER = 'INTEGER'
POWER = 'POWER'

IDENTIFIER = 'IDENTIFIER'
KEYWORD = 'KEYWORD'
EQUALS = 'EQUALS'

FLOAT = 'FLOAT'
DIGITS = '0123456789'

KEYWORDS = [
    'VAR'
]

LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return str(self.token.value)

class VarAccessNode:
    def __init__(self, var_name_token) -> None:
        self.var_name_token = var_name_token

class VarAssignNode:
    def __init__(self, var_name_token, value_node) -> None:
        self.var_name_token = var_name_token
        self.value_node = value_node

class BinaryOperation:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __repr__(self):
        return '({}, {}, {})'.format(self.left, self.operator, self.right)


class UnaryOperation:
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return '({} {})'.format(self.operator, self.right)


class Token:
    def __init__(self, value, type) -> None:
        self.value = value
        self.type = type
    
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
        

    def __repr__(self):
        if self.type not in [INTEGER, FLOAT]:
            return f'{self.type}'
        return f'{self.type}:{self.value}'
    

class Lexer:
    def __init__(self, expression):
        self.expression = expression
        self.current_index = -1
        self.tokens = []
        self.advance()

    def advance(self):
        self.current_index += 1
        if self.current_index >= len(self.expression):
            self.current_char = None
        else:
            self.current_char = self.expression[self.current_index]
    
    def get_tokens(self):
        while self.current_char is not None:
            if self.current_char in DIGITS:
                self.tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                self.tokens.append(self.make_identifier())
            elif self.current_char == ' ':
                self.advance()
            elif self.current_char == '+':
                self.tokens.append(Token(self.current_char, PLUS))
                self.advance()
            elif self.current_char == '-':
                self.tokens.append(Token(self.current_char, MINUS))
                self.advance()
            elif self.current_char == '*':
                self.tokens.append(Token(self.current_char, MULTIPLY))
                self.advance()
            elif self.current_char == '/':
                self.tokens.append(Token(self.current_char, DIVIDE))
                self.advance()
            elif self.current_char == '(':
                self.tokens.append(Token(self.current_char, LPAREN))
                self.advance()
            elif self.current_char == ')':
                self.tokens.append(Token(self.current_char, RPAREN))
                self.advance()
            elif self.current_char == '=':
                self.tokens.append(Token(self.current_char, EQUALS))
                self.advance()
            elif self.current_char == '^':
                self.tokens.append(Token(self.current_char, POWER))
                self.advance()

        return self.tokens
    
    def make_number(self):
        num = ''
        while self.current_char is not None and self.current_char in DIGITS or self.current_char == '.':
            num += self.current_char
            self.advance()
        if '.' in num:
            return Token(float(num), FLOAT)
        else:
            return Token(int(num), INTEGER)
    
    def make_identifier(self):
        identifier_str = ''
        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            identifier_str += self.current_char
            self.advance()
        
        token_type = KEYWORD if identifier_str in KEYWORDS else IDENTIFIER
        return Token(identifier_str, token_type)
    

class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.token_index = -1
        self.advance()
    
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def parse(self):
        return self.expr()
    
    def atom(self):
        token = self.current_token
        if token.type in (INTEGER, FLOAT):
            self.advance()
            return NumberNode(token)
        
        elif token.type == IDENTIFIER:
            self.advance()
            return VarAccessNode(token)
        
        elif token.type == LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type == RPAREN:
                self.advance()
                return expr
            else:
                return None
        else:
            return None
    
    def power(self):
        return self.bi_op(self.atom, (POWER,), self.factor)
    
    def factor(self):
        token = self.current_token
        if token.type in (PLUS, MINUS):
            self.advance()
            factor = self.factor()
            return UnaryOperation(token, factor)

        return self.power()

    def expr(self):
        if self.current_token.matches(KEYWORD, 'VAR'):
            self.advance()
            
            if self.current_token.type != IDENTIFIER:
                return None
            
            var_name = self.current_token

            self.advance()

            if self.current_token.type != EQUALS:
                return None
  
            self.advance()

            expr = self.expr()
            if not expr:
                return None
            
            return VarAssignNode(var_name, expr)
        
        return self.bi_op(self.term, (PLUS, MINUS))

    def term(self):
        return self.bi_op(self.factor, (MULTIPLY, DIVIDE))

    def bi_op(self, func_a, operations, func_b=None):
        if func_b == None:
            func_b = func_a
        left = func_a()
        while self.current_token.type in operations:
            op = self.current_token
            self.advance()
            right = func_b()
            left = BinaryOperation(left, op, right)

        return left
    

class Number:
    def __init__(self, value):
        self.value = value
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
    
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
    
    def divided_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value)
    
    def powered_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value)
    
    def __repr__(self) -> str:
        return str(self.value)

class Context:
    def __init__(self, display_name, parent=None) -> None:
        self.display_name = display_name
        self.parent = parent
        self.symbol_table = None
    

class SymbolTable:
    def __init__(self) -> None:
        self.symbols = {}
        self.parent = None
    
    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value
    
    def set(self, name, value):
        self.symbols[name] = value    
    
    def remove(self, name):
        del self.symbols[name]

class Interpreter:
    
    def visit(self, node):
        name = node.__class__.__name__

        if name == 'NumberNode':
            return self.visit_NumberNode(node)
        elif name == 'BinaryOperation':
            return self.visit_BinaryOperation(node)
        elif name == 'UnaryOperation':
            return self.visit_UnaryOperation(node)
        elif name == 'VarAssignNode':
            return self.visit_VarAssignNode(node)
        elif name == 'VarAccessNode':
            return self.visit_VarAccessNode(node)
        else:
            print(node)
            raise Exception(f'Unknown node: {name}')
    
    def visit_VarAccessNode(self, node, context):
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
        
        if not value:
            return None
        
        return value
    
    def visit_VarAssignNode(self, node, context):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node, context)
        context.symbol_table.set(var_name, value)
        return value
        

    def visit_NumberNode(self, node):
        return Number(node.token.value)
    
    def visit_UnaryOperation(self, node):
        if node.operator.type == PLUS:
            return self.visit(node.right)
        elif node.operator.type == MINUS:
            return self.visit(node.right).multiplied_by(Number(-1))
        else:
            raise Exception(f'Unknown operator {node.operator.type}')
    
    def visit_BinaryOperation(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator.type == PLUS:
            return left.added_to(right)
        elif node.operator.type == MINUS:
            return left.subtracted_by(right)
        elif node.operator.type == MULTIPLY:
            return left.multiplied_by(right)
        elif node.operator.type == DIVIDE:
            return left.divided_by(right)
        elif node.operator.type == POWER:  
            return left.powered_by(right)
             
        else:
            raise Exception(f'Unknown operator {node.operator.type}')

global_symbol_table = SymbolTable()

def evaluate(expression):
    lexer = Lexer(expression)
    result = lexer.get_tokens()
    logger.info(f'Lexerised result: {result}')

    parser = Parser(result)
    result = parser.parse()
    logger.info(f'Parsed result: {result}')

    interpreter = Interpreter()
    result = interpreter.visit(result)
    return result.value

if __name__ == '__main__':
    print(evaluate('VAR a = 2'))