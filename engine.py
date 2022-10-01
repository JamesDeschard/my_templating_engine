import codecs

from document import Document, Expression, Tag, Variable, RetrieveVarsFromExpression
from utils import (depth, find_deepest_value, find_specific_key,
                   get_closing_expression_index, get_closing_tag_index,
                   get_html_attributes, get_html_tag_name)


class Token:
    def __init__(self, type, content, index):
        self.type = type
        self.content = content
        self.index = index
        self.specs = self.get_specs()
    
    def get_specs(self):
        if 'endfor' in self.content:
            return 'ENDFOR'
        elif 'for' in self.content:
            return 'FOR'
        elif 'endif' in self.content:
            return 'ENDIF'
        elif 'if' in self.content:
            return 'IF'
        
        if self.type == 'TAG':
            return self.content
        
        if self.type == 'VARIABLE':
            return self.content

    def __repr__(self) -> str:
        return f'{self.type}:{self.specs}:{self.index}'

         
class Lexer:    
    """
    Time complexity: O(nlogn)
    """
    def __init__(self, template) -> None:
        self.template = template
        self.tokens = []
         
    def tokenize(self):   
        for index, char in enumerate(self.template):
            if index != len(self.template) -1 and char + self.template[index + 1] == '{%':
                content, pointer = str(), index + 2
                
                while self.template[pointer - 1] + self.template[pointer] != '%}':
                    content += self.template[pointer]
                    pointer += 1
                    
                content = self.template[index + 2 : pointer + 1]
                self.tokens.append(Token('EXPRESSION', content, index))
            
            elif index != len(self.template) - 1 and char + self.template[index + 1] == '{{':
                content, pointer = str(), index + 2
                
                while self.template[pointer - 1] +  self.template[pointer] != '}}':
                    content += self.template[pointer]
                    pointer += 1
                    
                self.tokens.append(Token('VARIABLE', content[:-1], index))
                     
            elif char == '<':
                name, pointer = str(), index
                
                while self.template[pointer] != '>':
                    name += self.template[pointer]
                    pointer += 1
                    
                self.tokens.append(Token('TAG', name + '>', index))

        return self.tokens
    
    
class Parser:
    """
    Time complexity: O(nlogn)
    
    """
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.tag_list = []
        
        self.current_index = []
        self.document = Document()
        self.limit = int()
    
    def add_tag_to_document(self, tag):
        if not self.current_index:
            self.document.tree[tag] = {}
                
        elif tag.start > self.current_index[-1].end:                            
            count = len([i for i in self.current_index if tag.start > i.end])
            self.current_index = self.current_index[:-count]
           
            if not self.current_index:
                self.document.tree.update({tag: {}})
                
            else:
                current_keys = find_specific_key(self.current_index[-1], self.document.tree)
                current_keys[tag] = {}                  
            
        elif tag.start > self.current_index[-1].start:                          
            current_keys = find_specific_key(self.current_index[-1], self.document.tree)
            
            if len(current_keys) >= 1:
                if list(current_keys.keys())[-1].end < tag.start:
                    current_keys[tag] = {}
                else:
                    current_val = find_deepest_value(current_keys)
                    current_val.update({tag: {}})
            else:
                current_keys[tag] = {}
                
            if tag.end > self.limit:
                self.limit = tag.end
            
        self.current_index.append(tag)

    def parse(self, tokens):      
        for index, token in enumerate(tokens):
            if token.type == 'TAG' and '</' not in token.content:   
                tag_name = get_html_tag_name(token)                                   
                tag_index = get_closing_tag_index(index, tag_name, tokens) 
                
                if tag_index:
                    closing_tag = self.tokens[tag_index]
                    start, end = token.index, closing_tag.index  
                else:
                    start, end = token.index, token.index + len(token.content)
                
                html_attrs = get_html_attributes(token)
                self.add_tag_to_document(Tag(tag_name, start, end, html_attrs=html_attrs))
                    
            elif token.type == 'VARIABLE':
                name = token.content
                start, end = token.index, token.index + len(token.content)
                self.add_tag_to_document(tag = Variable(name, start, end))

            elif token.type == 'EXPRESSION' and 'END' not in token.specs:
                tag_index = get_closing_expression_index(index, token, tokens)
                name = token.content[:-2].strip()
                start, end = token.index, tokens[tag_index].index + len(tokens[tag_index].content)
                self.add_tag_to_document(Expression(name, start, end))
            
            else:
                continue
        
        return self.document


class Interpreter:
    def __init__(self, document, context) -> None:
        self.document = document
        self.context = context
        self.document.build_document()
        
        self.current_tag = str()
        self.document_string = str()
        
        self.render(self.document.tree)
    
    def reset_current_string(self):
        self.current_tag = str()
    
    def set_context(self, context):
        self.context = context
    
    def visit_tag(self, tag):
        current_string = tag.opening()
        if tag.content:
            self.reset_current_string()
            current_string += self.render(tag.content)
            
        return current_string + tag.closing()
    
    def visit_variable(self, variable):
        var_type = variable.__class__.__name__
        return RetrieveVarsFromExpression(var_type, variable.name, self.context).manager()
    
    def visit_expression(self, expression):
        expression_command, expression_condition = expression.evaluate_expression(self.context)
        if expression_command == 'if' and expression_condition:
            children = find_specific_key(expression, self.document.tree)
            return self.render(children)
        
        elif expression_command == 'for' and expression_condition:
            children = find_specific_key(expression, self.document.tree)
            looped_var, iterable_var = expression_condition
            original_context = self.context
            forloop_content = ''
            
            for iterable in iterable_var:
                self.set_context({looped_var: iterable})
                self.reset_current_string()
                forloop_content += self.render(children) 
                
            self.set_context(original_context)
            
            return forloop_content
        
        return ''

    def render(self, tag):
        for parent in tag.keys():
            if isinstance(parent, Tag):
                self.current_tag += self.visit_tag(parent)
            elif isinstance(parent, Variable):
                self.current_tag += self.visit_variable(parent)
            elif isinstance(parent, Expression):
                self.current_tag += self.visit_expression(parent)
            
            if parent == list(self.document.tree.keys())[-1]:
                self.document_string += self.current_tag
            
        return self.current_tag

        
def render_to_string(template, context):
    template = codecs.open(template, 'r', 'utf-8').read()
    result = Lexer(template).tokenize()
    result = Parser(result).parse(result)
    result = Interpreter(result, context)
    print()
    print(result.document_string)
    print()
    return result


                