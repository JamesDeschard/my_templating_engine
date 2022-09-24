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
    
    def get_closing_tag_name_and_index(self, start_index, token):
        tag_name = self.get_html_tag_name(token)
        
        if tag_name in SELF_CLOSING_TAGS:
            return tag_name, False
        
        count, new_tag = start_index + 1, 0
        
        while not all([self.tokens[count].specs == '</%s>' % tag_name, new_tag <= 0]):
            if '<%s' % tag_name in self.tokens[count].specs:
                new_tag += 1
            elif '</%s' % tag_name in self.tokens[count].specs:
                new_tag -= 1
            count += 1

        return tag_name, count
    
    def parse(self, tokens):
        current_index = 0
        current_depth = 0
        
        for i, token in enumerate(tokens):
            if token.type == 'TAG' and '</' not in token.content:                                      
                tag_name, count = self.get_closing_tag_name_and_index(i, token) 
                
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
                count = self.get_closing_expression_index(i, token, tokens)
                
                name = token.content[:-2].strip()
                start, end = token.index, tokens[count].index + len(tokens[count].content)
                tag = Expression(name, start, end)
            
            else:
                continue
            
            # Created a nested dict representing the AST
            print(tag.start, tag.end)
            if tag.start > current_index:
                current_depth += 1
            current_index = tag.end
            print(current_depth)
            self.tag_list.append(tag)
        
        print(self.tag_list)


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
                current_template_index += tag.start
            elif isinstance(tag, Variable):
                variable_content = self.evaluate_var(tag.name)
                break
        print(self.rendered_string)
           
    
    

                
def render_to_string(template, context):
    template = codecs.open(template, 'r', 'utf-8').read()
    result = Lexer(template).tokenize()
    result = Parser(result).parse(result)
    # result = Interpreter(result, template, context).interpret()
    return result




        
        
    