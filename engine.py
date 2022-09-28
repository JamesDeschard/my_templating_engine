import codecs

from document import Document, Expression, Tag, Variable
from utils import (Token, depth, find_deepest_value, find_specific_key,
                   get_closing_expression_index, get_closing_tag_index,
                   get_html_attributes, get_html_tag_name)

         
class Lexer:    
    """
    Time complexity: O(nlogn)
    """
    def __init__(self, template) -> None:
        self.template = template
        self.tokens = list()
         
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
        self.tag_list = list()
        
        self.current_index = list()
        self.document = Document()
        self.limit = int()
    
    def set_limit(self, tag):
        if tag.end > self.limit:
            self.limit = tag.end
            self.current_index.append(tag)
    
    def add_tag_to_document(self, tag):
        if not self.current_index:
            self.current_index.append(tag)
            self.document.tree[tag] = {}
                
        elif tag.start > self.current_index[-1].end:
            count = len([i for i in self.current_index if tag.start > i.end])
            self.current_index = self.current_index[:-count]
           
            if not self.current_index:
                self.document.tree.update({tag: {}})
                
            else:
                current_vals = find_specific_key(self.current_index[-1], self.document.tree)
                current_vals[tag] = {}
                    
            self.current_index.append(tag) 
            
        elif tag.start > self.current_index[-1].start:
            current_vals = find_specific_key(self.current_index[-1], self.document.tree)
            
            if len(current_vals) >= 1:
                if list(current_vals.keys())[-1].end < tag.start:
                    current_vals[tag] = {}
                else:
                    deepest = find_deepest_value(current_vals)
                    deepest.update({tag: {}})
            else:
                current_vals[tag] = {}
                
            self.set_limit(tag)
        
        return True

    def parse(self, tokens):      
        for index, token in enumerate(tokens):
            if token.type == 'TAG' and '</' not in token.content:   
                tag_name = get_html_tag_name(token)                                   
                count = get_closing_tag_index(index, tag_name, tokens) 
                
                if count:
                    closing_tag = self.tokens[count]
                    start, end = token.index, closing_tag.index  
                else:
                    start, end = token.index, token.index + len(token.content)
                    
                tag = Tag(tag_name, start, end, html_attributes=get_html_attributes(token))
                    
            elif token.type == 'VARIABLE':
                name = token.content
                start, end = token.index, token.index + len(token.content)
                tag = Variable(name, start, end)

            elif token.type == 'EXPRESSION' and 'END' not in token.specs:
                count = get_closing_expression_index(index, token, tokens)
                
                name = token.content[:-2].strip()
                start, end = token.index, tokens[count].index + len(tokens[count].content)
                tag = Expression(name, start, end)
            
            else:
                continue
            
            self.add_tag_to_document(tag)
        
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
        
    
    def render_tag(self, tag):
        is_variable = isinstance(tag, Variable)
        is_expression = isinstance(tag, Expression)
        
        if is_variable:
            return tag.get_variable_from_context(self.context)
        elif is_expression:
            return ''

        current_string = tag.opening()

        if tag.content:
            self.current_tag = str()
            current_string += self.render(tag.content)
            
        return current_string + tag.closing() 
            
    def render(self, tag):
        for parent in tag.keys():
            self.current_tag += self.render_tag(parent)
            
            if self.depth.get(parent) == 1 and parent == list(self.document.tree.keys())[-1]:
                self.document_string += self.current_tag
            
        return self.current_tag

        
                
      
def render_to_string(template, context):
    template = codecs.open(template, 'r', 'utf-8').read()
    result = Lexer(template).tokenize()
    result = Parser(result).parse(result)
    result = Interpreter(result, context)
    print(result.document_string)
    return result


                