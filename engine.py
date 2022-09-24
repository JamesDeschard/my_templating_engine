import codecs
import re 

from utils import Token, HtmlTag, Variable, Expression


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
        self.html_tree = dict()
    
    def create_ast(self, data):
        self.html_tree = {tag: list() for tag in self.tag_list}
        for i in range(len(data) - 1):
            counter = i + 1
            while data[i].end > data[counter].start:
                self.html_tree[data[i]].append(data[counter])
                counter += 1
                if counter >= len(data) - 1:
                    break
        
        return filter(lambda x: x[1] != [], self.html_tree.items())
    
    def parse(self, tokens):
        for i, token in enumerate(tokens):
            if token.type == 'TAG' and '</' not in token.content:                                      
                tag_name = re.findall(r'\w+', token.content)[0]
                closing_tag = list(filter(lambda x: x.content == '</%s>' % tag_name, tokens[i:]))       
                
                if closing_tag:
                    closing_tag = self.tokens.index(closing_tag[0])
                    start, end = token.index, self.tokens[closing_tag].index
                    tag = HtmlTag(tag_name, start, end)     
                else:
                    tag = HtmlTag(tag_name, token.index, token.index + len(token.content))
                    
            elif token.type == 'VARIABLE':
                start, end = token.index, token.index + len(token.content)
                tag = Variable(token.content, start, end)

            elif token.type == 'EXPRESSION' and 'END' not in token.specs:
                count, new_expression = i + 1, 0
                        
                while all([tokens[count].specs != 'END%s' % token.specs, new_expression != 0]):
                    if tokens[count].specs in ['FOR', 'IF']:
                        new_expression += 1
                    elif 'END' in tokens[count].specs:
                        new_expression -= 1
                    count += 1

                content = token.content[:-2].strip()
                end = tokens[count].index + len(tokens[count].content)
                tag = Expression(content, token.index, end)
            
            if tag not in self.tag_list:
                self.tag_list.append(tag)
                
        return dict(self.create_ast(self.tag_list))


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




        
        
    