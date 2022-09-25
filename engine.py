import codecs
from utils import (SELF_CLOSING_TAGS, Expression, HtmlTag, HtmlTree, Token,
                   Variable, get_html_attributes, get_html_tag_name,
                   recursive_lookup, get_closing_expression_index, get_closing_tag_index)


class Lexer:    
    """
    Time complexity: O(n) (need to add next() * while loop pointer)
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
    Time complexity: O(n^2)
    
    """
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.tag_list = list()
        
        self.current_index = []
        self.html_tree = HtmlTree().tree
        self.limit = 0
    
    def create_html_tree(self, tag):
        if not self.current_index:
            self.current_index.append(tag)
            self.html_tree[tag] = {}
                
        elif tag.start > self.current_index[-1].end:
            for index in range(len(self.current_index)):
                try:
                    if tag.start > self.current_index[index].end:
                        self.current_index.pop()
                except IndexError:
                    self.current_index.pop()
                    
            
            if not self.current_index:
                self.html_tree.update({tag: {}})
                
            else:
                current = recursive_lookup(self.current_index[-1], self.html_tree)
                current[tag] = {}
                    
            self.current_index.append(tag) 
            
        elif tag.start > self.current_index[-1].start < self.current_index[-1].end:
            current = recursive_lookup(self.current_index[-1], self.html_tree)
            
            nested = False
            for k, v in current.items():
                if k.end > tag.end:
                    v[tag] = {}
                    nested = True
                    
            if not nested:
                current[tag] = {}
                
            if tag.end > self.limit:
                self.limit = tag.end
                self.current_index.append(tag)

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
                    
                tag = HtmlTag(tag_name, start, end, get_html_attributes(token))
                    
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
            
            self.create_html_tree(tag)
        
        print(self.html_tree)
        return self.html_tree


class Interpreter:
    def __init__(self, html_tree, template, context) -> None:
        self.html_tree = html_tree
        self.template = template
        self.context = context
        self.rendered_string = str()
    
    def evaluate_var(self, var):
        var = var.split('.')
        if len(var) == 1:
            var = self.context.get(var[0])
        else:
            var = self.context.get(var[0])
            for i in range(len(var)):
                var = var.get(var[i])
                
        return var if var else None
        
    
    def interpret(self):
        html_heap = list()
        current_template_index = 0
        
        for tag, children in self.html_tree.items():
            if isinstance(tag, HtmlTag):
                continue
            elif isinstance(tag, Variable):
                continue
            else:
                continue
        print(self.rendered_string)
           
    
    

                
def render_to_string(template, context):
    template = codecs.open(template, 'r', 'utf-8').read()
    result = Lexer(template).tokenize()
    result = Parser(result).parse(result)
    # result = Interpreter(result, template, context).interpret()
    return result




        
        
        
    