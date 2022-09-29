import pprint
import string

from evaluate import evaluate
from utils import SELF_CLOSING_TAGS


class Document:
    def __init__(self) -> None:
        self.tree = dict()
        
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
    # self.content should be called self.children
    # Make content attribute to register content which is not in child tag
    def __init__(self, name, start, end, content=dict(), html_attrs=list()) -> None:
        self.name = name
        self.start = start
        self.end = end
        
        self.content = content
        self.html_attrs = html_attrs
    
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
        self.variable_name = name
        self.start = start
        self.end = end
    
    def get_variable_from_context(self, context):
        return context.get(self.variable_name, '')

    def __repr__(self) -> str:
        return self.variable_name
    
    
class Expression:
    def __init__(self, expression, start, end) -> None:
        self.expression = expression
        self.start = start
        self.end = end
        
        self.context = None
    
    def set_context(self, context):
        self.context = context
    
    def get_variable_from_context(self, variable, context=None):
        if context == None:
            context = self.context
        return context.get(variable, False)
    
    def get_variable_from_expression(self, expression):
        def get_tokens(tag):
            allowed_chars = string.ascii_letters +  '.'
            return not tag.startswith('"') and not tag.endswith('"') and all([l in allowed_chars for l in tag])
        
        assumed_vars = list(filter(lambda tag: get_tokens(tag), expression.split()))
        existing_vars = []
        
        for var in assumed_vars:
            var = var.split('.')
            if len(var) == 1:
                existing_vars.append(self.get_variable_from_context(var[0], self.context))
            else:
                count = 0
                context = self.context
                while count != len(var):
                    context = self.get_variable_from_context(var[count], context)
                    count += 1
                    
                existing_vars.append(context)
                
        return existing_vars

    def check_expression_validity(self, expression, ):
        self.get_variable_from_expression(expression)
        # expression = evaluate(expression)
        # expression = True if expression else False
        # return expression
        return ""
        
    def evaluate_expression(self, context):
        self.set_context(context)
        expression_command = self.expression.split()[0]
        expression_content = self.expression[len(expression_command):].strip()

        if expression_command == 'for':
            pass
        elif expression_command == 'if':
            return self.check_expression_validity(expression_content)
        else:
            raise ValueError(f"Invalid expression command: {expression_command}")

    def __repr__(self) -> str:
        return self.expression
