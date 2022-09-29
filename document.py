import pprint

from evaluate_expression import evaluate
from utils import SELF_CLOSING_TAGS, OPERATORS


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
    def __init__(self, name, start, end, content=dict(), html_attributes=list()) -> None:
        self.name = name
        self.start = start
        self.end = end
        
        self.content = content
        self.html_attributes = html_attributes
    
    def opening(self):
        if self.html_attributes: 
            return f'''<{self.name} {' '.join(a[0] + '=' + '"' + a[1] + '"' for a in self.html_attributes)}>'''
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
    
    def get_variable(self, variable, context):
        return context.get(variable, False)
    
    def check_if_expression_validity(self, expression, context):
        expression = evaluate(expression)
        expression = True if expression else False
        return expression
        
    def evaluate_expression(self, context):
        expression_command = self.expression.split()[0]
        expression_content = self.expression[len(expression_command):].strip()

        if expression_command == 'for':
            pass
        elif expression_command == 'if':
            self.check_if_expression_validity(expression_content, context)
        else:
            raise ValueError(f"Invalid expression command: {expression_command}")

    def __repr__(self) -> str:
        return self.expression
