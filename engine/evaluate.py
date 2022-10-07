from glob import escape
import logging
import string
from logging.config import IDENTIFIER

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('LANGUAGE')

### GRAMMAR ###

"""
expr        :   KEYWORD: VAR IDENTIFIER EQ expr
            :   comp-expr ((KEYWORD: AND | KEYWORD: OR) comp-expr)*
            
compr-r     :   NOT comp-expr	
            :   arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*	
            
arith-expr  :   term ((PLUS | MINUS) term)*

term        :   factor ((MUL | DIV) factor)*

factor      :   (PLUS | MINUS) factor
            :    power

power       :   atom (POW factor)*

atom        :   INT|FLOAT|STRING|IDENTIFIER
            :   LPAREN expr RPAREN
"""

### SYNTAXE ###

"""
mathematical operations : +, -, *, /,^
logical operations : ==, !=, >, <, >=, <=
comparison operations : and, or, not
set variables : VAR (identifier = string) = (expression)
"""

###CONTANTS ###

PLUS = 'PLUS'
MINUS = 'MINUS'
MULTIPLY = 'MUL'
DIVIDE = 'DIV'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
INTEGER = 'INTEGER'
POWER = 'POWER'

STRING = 'STRING'

DOUBLE_EQUALS = 'DOUBLE_EQUALS'
NOT_EQUALS = 'NOT_EQUALS'
LESS_THAN = 'LESS_THAN'
GREATER_THAN = 'GREATER_THAN'
LESS_THAN_OR_EQUAL = 'LESS_THAN_OR_EQUAL'
GREATER_THAN_OR_EQUAL = 'GREATER_THAN_OR_EQUAL'

IDENTIFIER = 'IDENTIFIER'
KEYWORD = 'KEYWORD'
EQUALS = 'EQUALS'

FLOAT = 'FLOAT'
DIGITS = '0123456789'

KEYWORDS = [
    'VAR',
    'AND',
    'OR',
    'NOT',
]

LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


### NODES ###

class StringNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return str(self.token.value)

class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return str(self.token.value)

class VarAccessNode:
    def __init__(self, var_name_token) -> None:
        self.var_name_token = var_name_token
    
    def __repr__(self) -> str:
        return f'{self.var_name_token}'

class VarAssignNode:
    def __init__(self, var_name_token, value_node) -> None:
        self.var_name_token = var_name_token
        self.value_node = value_node
        
    def __repr__(self) -> str:
        return f'{self.var_name_token} = {self.value_node}'

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
    
    
### LEXER ###

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
            elif self.current_char == '"':
                self.tokens.append(self.make_string())
            elif self.current_char in LETTERS:
                self.tokens.append(self.make_identifier())
            elif self.current_char == ' ':
                self.advance()
            elif self.current_char == '"':
                self.tokens.append(self.make_string())
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
            elif self.current_char == '^':
                self.tokens.append(Token(self.current_char, POWER))
                self.advance()
            elif self.current_char == '!':
                self.tokens.append(self.make_not_equals())
            elif self.current_char == '=':
                self.tokens.append(self.make_equals())
            elif self.current_char == '<':
                self.tokens.append(self.make_less_than())
                self.advance()
            elif self.current_char == '>':
                self.tokens.append(self.make_greater_than())
                self.advance()

        return self.tokens

    def make_string(self):
        string = ''
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False

        return Token(string, STRING)
    
    def make_less_than(self):
        token_type = LESS_THAN
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            token_type = LESS_THAN_OR_EQUAL
            
        return Token(token_type, token_type)
    
    def make_greater_than(self):
        token_type = GREATER_THAN
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            token_type = GREATER_THAN_OR_EQUAL
            
        return Token(token_type, token_type)
    
    def make_equals(self):
        token_type = EQUALS
        self.advance()
        
        if self.current_char == '=':
            self.advance()
            token_type = DOUBLE_EQUALS
        return Token(token_type, token_type)

    def make_not_equals(self):
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(NOT_EQUALS, NOT_EQUALS)
        self.advance()
        return None
        
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
 
 
### PARSER ###   

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
        
        if token.type == STRING:
            self.advance()
            return StringNode(token)
        
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

    def term(self):
        return self.bi_op(self.factor, (MULTIPLY, DIVIDE))
    
    def arith_expr(self):
        return self.bi_op(self.term, (PLUS, MINUS))
    
    def comp_expr(self):
        if self.current_token.matches(KEYWORD, 'NOT'):
            op_token = self.current_token
            self.advance()
            node = self.comp_expr()
            return UnaryOperation(op_token, node)
        
        return self.bi_op(self.arith_expr, (
            DOUBLE_EQUALS, NOT_EQUALS, LESS_THAN, LESS_THAN_OR_EQUAL, GREATER_THAN, GREATER_THAN_OR_EQUAL
        ))
    
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
        
        return self.bi_op(self.comp_expr, ((KEYWORD, 'AND'), (KEYWORD, 'OR')))

    def bi_op(self, func_a, operations, func_b=None):
        if func_b == None:
            func_b = func_a
            
        left = func_a()
        
        while self.current_token.type in operations or (self.current_token.type, self.current_token.value) in operations:
            op = self.current_token
            self.advance()
            right = func_b()
            left = BinaryOperation(left, op, right)

        return left


### INTERPRETER ### 


class Number:
    def __init__(self, value):
        self.value = value
        self.set_context()
    
    def set_context(self, context=None):
        self.context = context
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context)
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context)
    
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context)
    
    def divided_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value).set_context(self.context)
    
    def powered_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context)
        
    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context)
    
    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context)
    
    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context)
    
    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context)
    
    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context)
    
    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context)
    
    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context)
    
    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context)
    
    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context)
    
    def __repr__(self) -> str:
        return str(self.value)
    
    
class String:
    def __init__(self, value):
        self.value = value
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context)
    
    def get_comparison_eq(self, other):
        return Number(self.value == other.value).set_context(self.context)

    def get_comparison_ne(self, other):
        return Number(self.value != other.value).set_context(self.context)


    def __repr__(self):
        return f'"{self.value}"'


class Context:
    def __init__(self, display_name, parent=None) -> None:
        self.display_name = display_name
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
    
    def visit(self, node, context):
        name = node.__class__.__name__

        if name == 'NumberNode':
            return self.visit_NumberNode(node, context)
        elif name == 'BinaryOperation':
            return self.visit_BinaryOperation(node, context)
        elif name == 'UnaryOperation':
            return self.visit_UnaryOperation(node, context)
        elif name == 'VarAssignNode':
            return self.visit_VarAssignNode(node, context)
        elif name == 'VarAccessNode':
            return self.visit_VarAccessNode(node, context)
        elif name == 'StringNode':
            return self.visit_StringNode(node, context)
        else:
            raise Exception(f'Unknown node: {name}')
    
    def visit_StringNode(self, node, context):
        return String(node.token.value).set_context(context)
    
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
        
    def visit_NumberNode(self, node, context):
        return Number(node.token.value).set_context(context)
    
    def visit_UnaryOperation(self, node, context):
        if node.operator.type == PLUS:
            return self.visit(node.right, context)
        elif node.operator.type == MINUS:
            return self.visit(node.right, context).multiplied_by(Number(-1))
        elif node.operator.type.matches(KEYWORD, 'NOT'):
            return self.visit(node.right, context).notted()
        else:
            raise Exception(f'Unknown operator {node.operator.type}')
    
    def visit_BinaryOperation(self, node, context):
        left = self.visit(node.left, context)
        right = self.visit(node.right, context)

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
        elif node.operator.type == DOUBLE_EQUALS:
            return left.get_comparison_eq(right)
        elif node.operator.type == NOT_EQUALS:
            return left.get_comparison_ne(right)
        elif node.operator.type == LESS_THAN:
            return left.get_comparison_lt(right)
        elif node.operator.type == LESS_THAN_OR_EQUAL:
            return left.get_comparison_lte(right)
        elif node.operator.type == GREATER_THAN:
            return left.get_comparison_gt(right)
        elif node.operator.type == GREATER_THAN_OR_EQUAL:
            return left.get_comparison_gte(right)   
        elif node.operator.matches(KEYWORD, 'AND'):
            return left.anded_by(right)
        elif node.operator.matches(KEYWORD, 'OR'):
            return left.ored_by(right)
        else:
            raise Exception(f'Unknown operator {node.operator.type}')


### MAIN ###


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))

def evaluate(expression):
    lexer = Lexer(expression)
    result = lexer.get_tokens()

    parser = Parser(result)
    result = parser.parse()
    
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(result, context)
    return result.value

if __name__ == '__main__':
    while True:
        text = input('>> ')
        result = evaluate(text)
        print(result)
