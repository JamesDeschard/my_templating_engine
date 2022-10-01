from asyncore import loop
import pprint
import string
import re

from evaluate import evaluate
from utils import SELF_CLOSING_TAGS, RetrieveVarsFromExpression


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
        self.name = name
        self.start = start
        self.end = end
    
    def __repr__(self) -> str:
        return self.name
    
    
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
        
        elif expression_command == 'if':
            expression = RetrieveVarsFromExpression(expression_command, expression_content, self.context).manager()
            evaluation = evaluate(expression)
            evaluation = True if evaluation else False
            return expression_command, evaluation
            
        else:
            raise ValueError(f"Invalid expression command: {expression_command}")

    def __repr__(self) -> str:
        return self.expression
