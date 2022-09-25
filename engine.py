import codecs
import re

from utils import SELF_CLOSING_TAGS, Expression, HtmlTag, Token, Variable


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
    Time complexity: O(n^2)
    
    """
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.tag_list = list()
    
    def get_html_tag_name(self, token):
        return re.findall(r'\w+', token.content)[0]

    def get_html_attributes(self, token):
        return re.findall(r"""(\w+)=["']?((?:.(?!["']?\s+(?:\S+)=|\s*\/?[>"']))+.)["']?""", token.content)
    
    def get_closing_expression_index(self, start_index, token, tokens):
        count, new_expression = start_index + 1, 0
                        
        while not all([tokens[count].specs == 'END%s' % token.specs, new_expression <= 0]):
            if tokens[count].specs in ['FOR', 'IF']:
                new_expression += 1
            elif 'END' in tokens[count].specs:
                new_expression -= 1
            count += 1
         
        return count
    
    def get_closing_tag_index(self, start_index, tag_name):        
        if tag_name in SELF_CLOSING_TAGS:
            return False
        
        count, new_tag = start_index + 1, 0
        
        while not all([self.tokens[count].specs == '</%s>' % tag_name, new_tag <= 0]):
            if '<%s' % tag_name in self.tokens[count].specs:
                new_tag += 1
            elif '</%s' % tag_name in self.tokens[count].specs:
                new_tag -= 1
            count += 1

        return count

    def parse(self, tokens):
        current_index = []
        current_depth = {}
        limit = 0
        
        for index, token in enumerate(tokens):
            if token.type == 'TAG' and '</' not in token.content:   
                tag_name = self.get_html_tag_name(token)                                   
                count = self.get_closing_tag_index(index, tag_name) 
                
                if count:
                    closing_tag = self.tokens[count]
                    start, end = token.index, closing_tag.index  
                else:
                    start, end = token.index, token.index + len(token.content)
                    
                tag = HtmlTag(tag_name, start, end, attributes=self.get_html_attributes(token))
                    
            elif token.type == 'VARIABLE':
                name = token.content
                start, end = token.index, token.index + len(token.content)
                tag = Variable(name, start, end)

            elif token.type == 'EXPRESSION' and 'END' not in token.specs:
                count = self.get_closing_expression_index(index, token, tokens)
                
                name = token.content[:-2].strip()
                start, end = token.index, tokens[count].index + len(tokens[count].content)
                tag = Expression(name, start, end)
            
            else:
                continue
            
            print(tag.start, tag.end)
            
            # Create a nested dict representing the AST
            
            if not current_index:
                print('CASE 1')
                current_index.append(tag)
                current_depth[tag] = ''
                
            elif tag.start > current_index[-1].end:
                print('CASE 2')
                for index in range(len(current_index)):
                    if tag.start > current_index[index].end:
                        current_index.remove(current_index[index])
                
                if not current_index:
                    current_depth.update({tag: {}})
                else:
                    current = self.recursive_lookup(current_index[-1], current_depth)
                    current[tag] = {}
                        
                current_index.append(tag) 
                
            elif tag.start > current_index[-1].start < current_index[-1].end:
                print('CASE 3')
                print(current_index[-1])
                current = self.recursive_lookup(current_index[-1], current_depth)
                current[tag] = {}
                if tag.end > limit:
                    limit = tag.end
                    current_index.append(tag)
                    
            print(current_depth)
    
    def recursive_lookup(self, k, d):
        if k in d: 
            return d[k]
        for v in d.values():
            if isinstance(v, dict):
                a = self.recursive_lookup(k, v)
                if a is not None: 
                    return a
        return None
                



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




        
        
    