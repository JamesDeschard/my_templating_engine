import codecs
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
        
        self.expression_start = True
        self.expression_end = False
        
        self.current_expression_index = 0
        self.current_var_index = 0
    
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
        for index, char in enumerate(self.template):
            if char == '{':
                if self.template[index + 1] in '{%':
                    if self.template[index + 1] == '%':
                        if self.expression_start:
                            self.current_expression_index = index + 2
                            self.tokens.append([EXPRESSION_START, self.current_expression_index])
                            self.expression_start = False
                        else:
                            self.expression_start = True
                            
                    else:
                        self.current_var_index = index + 2
                        self.expression_start = False
                        
            elif char == '}':
                if self.template[index - 1] in '%}':
                    if self.template[index - 1] == '%':
                        if self.expression_end:
                            self.tokens.append([EXPRESSION_END, index -1]) 
                            self.expression_end = False
                        else:
                            self.tokens.append(self.tokenize_expression(self.template[self.current_expression_index:index - 1]))
                            self.expression_end = True
                    else:
                        self.tokens.append(self.tokenize_expression(self.template[self.current_var_index:index - 1]))
            
            elif char == '<' and not self.expression_start:
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
        for expression in self.parsed_data:
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
                
                self.template = self.template[0:indexes[0]] + forloop_data + self.template[indexes[1]:]
                # Update rest of indexes by length of forloop_data
                
        return self.template
                                

def render_to_string(template, context):
    template = codecs.open(template, 'r', 'utf-8').read()
    result = Lexer(template).tokenize()
    result = Parser(result, template).parse()
    result = Interpreter(result, template, context).read()
    return result


def get_json_data():
    with open('data.json') as f:
        return json.load(f)


def main():
    template = 'index.html'
    context = {
        'posts': get_json_data()
    }
    return render_to_string(template, context)


if __name__ == '__main__':
    print(main())
