# Contstants

class Token:
    def __init__(self, type, content, index):
        self.type = type
        self.content = content
        self.index = index
        self.specs = self.get_specs()
    
    def get_specs(self):
        if 'endfor' in self.content:
            return 'ENDFOR'
        elif 'for' in self.content:
            return 'FOR'
        elif 'endif' in self.content:
            return 'ENDIF'
        elif 'if' in self.content:
            return 'IF'
        
        if self.type == 'TAG':
            return self.content
        
        if self.type == 'VARIABLE':
            return self.content

    def __repr__(self) -> str:
        return f'{self.type}:{self.specs}:{self.index}'


class HtmlTree:
    def __init__(self) -> None:
        self.tree = list()
        
class HtmlTag:
    def __init__(self, name, start, end, content=list()) -> None:
        self.name = name
        self.start = start
        self.end = end
        
        self.content = content

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
    