SELF_CLOSING_TAGS = ['DOCTYPE','area', 'base', 'br', 'col', 'embed', 'hr', 'img','input', 'link', 'meta', 'param', 'source', 'track', 'wbr']


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
    def __init__(self, tags) -> None:
        self.tree = {tag: list() for tag in tags}
        self.ast = self.create_ast(tags)
        
        
class HtmlTag:
    def __init__(self, name, start, end, html_attributes = dict()) -> None:
        self.name = name
        self.start = start
        self.end = end
        
        self.html_attributes = html_attributes
    
    def tag_opening(self):
        return f"<{self.name} {' '.join(a[0] + '=' + a[1] for a in self.html_attributes)}>"
    
    def tag_closing(self):
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
    