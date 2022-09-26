import pprint

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
                                                    
    def pretty_print(self):
        return pprint.pprint(self.tree)
        
        
class Tag:
    def __init__(self, name, start, end, content=dict(), html_attributes=list()) -> None:
        self.name = name
        self.start = start
        self.end = end
        
        self.content = content
        self.html_attributes = html_attributes
    
    def opening(self):
        if self.html_attributes: 
            return f'''<{self.name} {' '.join(a[0] + '=' + a[1] for a in self.html_attributes)}>'''
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
        self.name = name
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return self.name
    
    
class Expression:
    def __init__(self, name, start, end) -> None:
        self.name = name
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return self.name
