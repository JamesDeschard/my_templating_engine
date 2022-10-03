import copy
import os

from document import (Document, Expression, RetrieveVarsFromExpression, Tag,
                      Variable)
from utils import (add_tabulation_and_line_breaks, depth, find_deepest_value,
                   find_specific_key, get_closing_expression_index,
                   get_closing_tag_index, get_html_attributes,
                   get_html_tag_name, get_template)

EXPRESSION = 'EXPRESSION'
VARIABLE = 'VARIABLE'
TAG = 'TAG'
EXTENDS = 'EXTENDS'


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
        elif 'elif' in self.content:
            return 'ELIF'
        elif 'if' in self.content:
            return 'IF'
        elif 'else' in self.content:
            return 'ELSE'
        elif 'endblock' in self.content:
            return 'ENDBLOCK'
        elif 'block' in self.content:
            return 'BLOCK'
        elif 'extends' in self.content:
            return 'EXTENDS'
        
        if self.type == 'TAG':
            return self.content
        
        if self.type == 'VARIABLE':
            return self.content

    def __repr__(self) -> str:
        return f'{self.type}:{self.specs}:{self.index}'

         
class Lexer:    
    """
    Time complexity: O(n)
    One iteration over the self.template variable.
    """
    def __init__(self, template) -> None:
        self.template = template
        self.tokens = []
        
        self._index = -1
        self.current_char = None
        self.advance()
    
    def advance(self):
        self._index += 1
        if self._index >= len(self.template):
            self.current_char = None
        else:
            self.current_char= self.template[self._index]
    
    def set_start_index_and_content(self, tag=False):
        if not tag:
            self.advance()
            return self._index - 1, ''
    
    def make_expression(self):
        self.advance()
        
        if self.current_char == '%':
            start_index, content= self.set_start_index_and_content()
            
            while self.current_char + self.template[self._index + 1] != '%}':
                content += self.current_char
                self.advance()
                
            self.tokens.append(Token(EXPRESSION, content, start_index))
            
        elif self.current_char == '{':
            self.make_variable()

    def make_variable(self):
        start_index, content= self.set_start_index_and_content()
        
        while self.current_char + self.template[self._index + 1] != '}}':
            content += self.current_char
            self.advance()
              
        self.tokens.append(Token(VARIABLE, content, start_index))
    
    def make_tag(self):
        start_index, content= self.set_start_index_and_content()
        content += '<'

        while self.current_char != '>':
            content += self.current_char
            self.advance()
            
        self.tokens.append(Token(TAG, content + '>', start_index))
        
    def tokenize(self):   
        while self.current_char is not None:
            if self.current_char == '{':
                self.make_expression()
            elif self.current_char == '<':
                self.make_tag()
            else:
                self.advance()
        
        return self.tokens
    
    
class Parser:
    """
    Time complexity: O(n) ??? nlogn?
    
    """
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.tag_list = []
        
        self.current_sibling = []
        self.document = Document()
        self.limit = 0
        
    def set_limit(self, tag):
        if tag.end > self.limit:
            self.limit = tag.end
    
    def add_new_child(self, parent, child):
        parent[child] = {} 
        
    def add_tag_to_document(self, tag):
        if not self.current_sibling:
            # Add first tag to document
            self.add_new_child(self.document.tree, tag)
                
        elif tag.start > self.current_sibling[-1].end:    
            # Tag is not a child of the current index                                    
            count = len([i for i in self.current_sibling if tag.start > i.end])
            self.current_sibling = self.current_sibling[:-count]
           
            if not self.current_sibling:
                self.document.tree.update({tag: {}})
                
            else:
                parent = find_specific_key(self.current_sibling[-1], self.document.tree)
                self.add_new_child(parent, tag)                  
            
        elif tag.start > self.current_sibling[-1].start: 
            # Tag is a child of the current index                        
            parents = find_specific_key(self.current_sibling[-1], self.document.tree)
            
            if len(parents) >= 1:
                if list(parents.keys())[-1].end < tag.start:
                    self.add_new_child(parents, tag) 
                else:
                    parent = find_deepest_value(parents)
                    parent.update({tag: {}})
            else:
                self.add_new_child(parents, tag)
                
            self.set_limit(tag)
            
        self.current_sibling.append(tag)

    def parse(self, tokens):      
        for index, token in enumerate(tokens):
            if token.type == TAG and '</' not in token.content:   
                tag_name = get_html_tag_name(token)                                   
                tag_index = get_closing_tag_index(index, tag_name, tokens) 
                
                if tag_index:
                    closing_tag = self.tokens[tag_index]
                    start, end = token.index, closing_tag.index  
                else:
                    start, end = token.index, token.index + len(token.content)
                
                html_attrs = get_html_attributes(token)
                self.add_tag_to_document(Tag(tag_name, start, end, html_attrs=html_attrs))
                    
            elif token.type == VARIABLE:
                name = token.content
                start, end = token.index, token.index + len(token.content)
                self.add_tag_to_document(Variable(name, start, end))

            elif token.type == EXPRESSION and 'END' not in token.specs:                    
                tag_index = get_closing_expression_index(index, token, tokens)
                name = token.content.strip()
                start, end = token.index, tokens[tag_index].index + len(tokens[tag_index].content)
                self.add_tag_to_document(Expression(name, start, end))
            
            elif token.specs == EXTENDS:
                extends = token.content.split()[-1]
                extends = extends.replace('"', '').replace("'", '')
                if extends not in os.listdir('templates'):
                    raise Exception(f'"{extends}" does not exist in templates folder')
                self.document.extends_another_file = extends        
                
                
            else:
                continue
            
        return self.document


class Interpreter:
    def __init__(self, document, context) -> None:
        self.document = document
        self.context = context
        self.document.build_document()
        self.depth = depth(self.document.tree)
        
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
        
        tabulation = add_tabulation_and_line_breaks(tag.closing(), self.depth.get(tag) - 1) 
        current_string += tabulation
        return current_string 
    
    def visit_variable(self, variable):
        var_type = variable.__class__.__name__
        return RetrieveVarsFromExpression(var_type, variable.name, self.context).manager()
    
    def visit_expression(self, expression):
        expression_command, expression_condition = expression.evaluate_expression(self.context)
        children = find_specific_key(expression, self.document.tree)
        self.reset_current_string()
        
        if expression_command in ['if', 'elif', 'else'] and expression_condition:
            return self.render(children)
        
        elif expression_command == 'for' and expression_condition:
            looped_var, iterable_var = expression_condition
            
            original_context = self.context
            forloop_content = ''
            
            for iterable in iterable_var:
                self.set_context({looped_var: iterable})
                self.reset_current_string()
                forloop_content += self.render(children) 
                
            self.set_context(original_context)
            return forloop_content
        
        elif expression_command == 'block':
            content = self.render(children)
            content = (expression_condition, content)
            if self.document.extends_another_file:
                self.document.blocks[self.document.extends_another_file] = content
                document = copy.copy(self.document.blocks)
                
                for template in document.keys():
                    document = ReadDocument().build(template, self.context)
                    result = document.document.blocks
                    self.document.blocks.update(result)
                              
        return ''

    def render(self, tag):
        for parent in tag.keys():
            if isinstance(parent, Tag):
                content = self.visit_tag(parent)
                tabulation = self.depth.get(parent) - 1
                self.current_tag += add_tabulation_and_line_breaks(content, tabulation)
            elif isinstance(parent, Variable):
                self.current_tag += self.visit_variable(parent)
            elif isinstance(parent, Expression):
                self.current_tag += self.visit_expression(parent)
            
            if parent == list(self.document.tree.keys())[-1]:
                self.document_string += self.current_tag
                
            
        return self.current_tag


class ReadDocument:
         
    def get_template(self, template):
        template = get_template(template)
        if not template:
            raise Exception('Template does not exist')
        return template
    
    def build(self, template, context):
        template = self.get_template(template)
        result = Lexer(template).tokenize()
        result = Parser(result).parse(result)
        result = Interpreter(result, context)
        return result
    
    def build_blocks(self, blocks):
        for template, (block_name, block_content) in blocks.items():
            pass


def render_to_string(template, context):
    reader = ReadDocument()
    document = reader.build(template, context)
    reader.build_blocks(document.document.blocks)
    return document
     