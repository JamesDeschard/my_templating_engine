import pprint

from evaluate_expression import calc
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
    
    # Add content attrs and build functions

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
        expression = expression.split()
        
        if len(expression) == 1:
            expression = expression[0]
            if expression == 'True':
                return True
            elif all(e for e in expression if e.isalpha()):
                return self.get_variable(expression, False)
            else:
                return False

        elif len(expression) == 3 and expression[1] in OPERATORS:
            print('EVALUATE CONDITION, OPERATOR, CONDITION')
            # Get both variables and run calc on them
            
        else:
            raise ValueError("Invalid expression: %s" % self.expression)
    
    def evaluate_expression(self, context):
        expression_command = self.expression.split()[0].lower()
        expression_content = self.expression[len(expression_command):].strip().lower()

        if expression_command == 'for':
            pass
        elif expression_command == 'if':
            self.check_if_expression_validity(expression_content, context)
        else:
            raise ValueError(f"Invalid expression command: {expression_command}")

    def __repr__(self) -> str:
        return self.expression
