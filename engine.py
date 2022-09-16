import codecs
import copy
import json
import re

EXPRESSION_START = 'EXPRESSION_START'
EXPRESSION_END = 'EXPRESSION_END'

VAR_START = 'VAR_START'
VAR_END = 'VAR_END'

class Lexer:    
    def __init__(self, template) -> None:
        self.template = template
        self.tokens = []
    
    def tokenize_expression(self, expression):
        expression = expression.strip()
        tokens = list()
        
        if 'endfor' in expression:
            return ['ENDFOR']
            
        elif 'for' in expression:
            tokens.append('FORLOOP')
            variable = re.findall(r'\w+$', expression)[0]
            tokens.append(variable)
            return tokens
        
        else:
            return ['VARIABLE', expression]
        
    def tokenize(self):
        expression_start = True
        expression_end = False
        
        current_expression_index = 0
        current_var_index = 0
        
        for index, char in enumerate(self.template):
            if char == '{':
                if self.template[index + 1] in '{%':
                    if self.template[index + 1] == '%':
                        if expression_start:
                            current_expression_index = index + 2
                            self.tokens.append([EXPRESSION_START, current_expression_index])
                            expression_start = False
                        else:
                            expression_start = True
                            
                    else:
                        current_var_index = index + 2
                        expression_start = False
                        
            elif char == '}':
                if self.template[index - 1] in '%}':
                    if self.template[index - 1] == '%':
                        if expression_end:
                            self.tokens.append([EXPRESSION_END, index -1]) 
                            expression_end = False
                        else:
                            self.tokens.append(self.tokenize_expression(self.template[current_expression_index:index - 1]))
                            expression_end = True
                    else:
                        self.tokens.append(self.tokenize_expression(self.template[current_var_index:index - 1]))
            
            elif char == '<' and not expression_start:
                count = index
                string = char
                tag = ''
                while string != '>':
                    string = self.template[count]
                    tag += string
                    count += 1
                self.tokens.append(['TAG', tag])

        return self.tokens

class Parser:
    def __init__(self, tokens, template) -> None:
        self.tokens = tokens
        self.template = template
        self.parsed_data = []
    
    def group_by_expression(self):
        indexes = [i for i, t in enumerate(self.tokens) if 'EXPRESSION' in t[0]]
        indexes = [indexes[i:i+2] for i in range(0, len(indexes), 2)]
        tokens = [self.tokens[i:j + 1] for i, j in indexes]
        return tokens
    
    def parse(self):
        expressions = self.group_by_expression()
        for tokens in expressions:
            expression = []
            indexes = tokens[0][1] -2, tokens[-1][1] + 2
            for token in tokens[1:-1]:
                if token[0] == 'FORLOOP':
                    expression.append('forloop__' + token[1])
                else:
                    expression.append(token[1])
            self.parsed_data.append({indexes: expression})
            
        return self.parsed_data
         
            
class Interpreter:
    def __init__(self, parsed_data, template, context) -> None:
        self.parsed_data = parsed_data
        self.template = template
        self.context = context
    
    
    def read(self):
        index_update = (0, 0)
        
        for expression in copy.copy(self.parsed_data):
            for indexes, operators in expression.items():
                tags = []
                for operator in operators:
                    if 'forloop' in operator:
                        context_var = operator.split('__')[1]
                        loop = True
                    elif operator.startswith('<'):
                        tags.append(operator)
                    else:
                        tags.append(operator.split('.')[-1])
                    
                        
                context_data = self.context.get(context_var)
                
                if loop:
                    forloop_data = ''
                    for data in context_data:
                        for tag in tags:
                            if tag.startswith('<'):
                                forloop_data += tag
                            else:
                                forloop_data += data.get(tag)
                
                indexes = (indexes[0] + index_update[0], indexes[1] + index_update[1])
                self.template = self.template[0:indexes[0]] + forloop_data + self.template[indexes[1]:]
                index_update = (indexes[0] + len(forloop_data),  indexes[1] + len(forloop_data))
                
                
        return self.template
                                

def render_to_string(template, context):
    template = codecs.open(template, 'r', 'utf-8').read()
    result = Lexer(template).tokenize()
    result = Parser(result, template).parse()
    result = Interpreter(result, template, context).read()
    return result


        
        
    