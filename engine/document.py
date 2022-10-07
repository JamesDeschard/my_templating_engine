import pprint
import re

from .evaluate import evaluate
from .utils import SELF_CLOSING_TAGS, RetrieveVarsFromExpression


class Document:
    def __init__(self, template) -> None:
        self.template = template
        self.tree = dict()
        self.var_replacement = 0
        
    def build_document(self, children=None):
        if children is None:
            children = self.tree
            
        for parent, children in children.items():
            parent.content = children
            if children:
                self.build_document(children)
            else:
                continue
                                                    
    def prettify(self):
        return pprint.pformat(self.tree)
        
        
class Tag:
    def __init__(self, 
                 name, 
                 start, 
                 end, 
                 inner_text,
                 context,
                 content=dict(), 
                 html_attrs=list(), 
        ) -> None:
        
        self.name = name
        self.start = start
        self.end = end
        self.context = context
        self.content = content
        self.inner_text = self.remove_tags_from_inner_text(inner_text)
        self.html_attrs = html_attrs
    
    def get_html_tag_name(token):
        return re.findall(r'\w+', token.content)[0]

    def get_html_attributes(token):
        return re.findall(r"""([^\s]+-?\w+)=["']?((?:.(?!["']?\s+(?:\S+)=|\s*\/?[>"']))+.)["']?""", token.content)
    
    def remove_tags_from_inner_text(self, inner_text):
        cleaner = re.compile(r'<[^>]+>')
        all_inner_tags = re.findall(cleaner, inner_text)
        is_nested = not len(all_inner_tags) == 2
        if not is_nested:
            cleaned_string = cleaner.sub('', inner_text).strip()
            return cleaned_string
        
        return ''
            
    def opening(self):
        if self.html_attrs: 
            return f'''<{self.name} {' '.join(a[0] + '=' + '"' + a[1] + '"' for a in self.html_attrs)}>'''
        return f"<{self.name}>"
    
    def closing(self):
        if self.name not in SELF_CLOSING_TAGS:
            return f"</{self.name}>"
        return ''

    def __repr__(self) -> str:
        return self.name


class Variable:
    def __init__(self, name, start, end) -> None:
        self.name = name
        self.start = start
        self.end = end
    
    def __repr__(self) -> str:
        return self.name
    
    
# IS_BLOCK keeps track of the current if/elif/else statement and its status
# If a new 'if' statement is found, the variable is reset

IS_BLOCK = {}   
    
class Expression:
    def __init__(self, expression, start, end) -> None:
        self.expression = expression
        self.start = start
        self.end = end
        
        self.context = None
    
    def set_context(self, context):
        self.context = context
           
    def evaluate_expression(self, context):
        self.set_context(context)
        expression_command = self.expression.split()[0]
        expression_content = self.expression[len(expression_command):].strip()

        if expression_command == 'for':
            loop_var, logical_operator, iterable_var = expression_content.split()
            
            if logical_operator != 'in':
                raise SyntaxError(f"Expected 'in' keyword, got {logical_operator}")
            
            iterable_var = RetrieveVarsFromExpression(expression_command, iterable_var, self.context).manager()
            return expression_command, (loop_var, iterable_var)
        
        elif expression_command in ['if', 'elif', 'else']:   
            if IS_BLOCK.get('if') == True:
                return expression_command, False
            
            elif expression_command == 'else':
                if not tuple(filter(lambda x: x, IS_BLOCK.values())):
                    return expression_command, True
                else: 
                    return expression_command, False
                
            expression = RetrieveVarsFromExpression(expression_command, expression_content, self.context).manager()
            evaluation = evaluate(expression)
            evaluation = True if evaluation else False
            IS_BLOCK[expression_command] = evaluation
            return expression_command, evaluation
          
        else:
            raise ValueError(f"Invalid expression command: {expression_command}")

    def __repr__(self) -> str:
        return self.expression
