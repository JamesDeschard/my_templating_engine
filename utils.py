import re

### CONSTANTS ###

SELF_CLOSING_TAGS = ['DOCTYPE','area', 'base', 'br', 'col', 'embed', 'hr', 'img','input', 'link', 'meta', 'param', 'source', 'track', 'wbr']


### FUNCTIONS ###

def recursive_lookup(desired_key, _dict):
    if desired_key in _dict: 
        return _dict[desired_key]
    
    for val in _dict.values():
        if isinstance(val, dict):
            res = recursive_lookup(desired_key, val)
            if res is not None: 
                return res
            
    return None


def get_html_tag_name(token):
    return re.findall(r'\w+', token.content)[0]


def get_html_attributes(token):
    return re.findall(r"""(\w+)=["']?((?:.(?!["']?\s+(?:\S+)=|\s*\/?[>"']))+.)["']?""", token.content)


def get_closing_expression_index(start_index, token, tokens):
    count, new_expression = start_index + 1, 0
                    
    while not all([tokens[count].specs == 'END%s' % token.specs, new_expression <= 0]):
        if tokens[count].specs in ['FOR', 'IF']:
            new_expression += 1
        elif 'END' in tokens[count].specs:
            new_expression -= 1
        count += 1
        
    return count

def get_closing_tag_index(start_index, tag_name, tokens):        
    if tag_name in SELF_CLOSING_TAGS:
        return False
    
    count, new_tag = start_index + 1, 0
    
    while not all([tokens[count].specs == '</%s>' % tag_name, new_tag <= 0]):
        if '<%s' % tag_name in tokens[count].specs:
            new_tag += 1
        elif '</%s' % tag_name in tokens[count].specs:
            new_tag -= 1
        count += 1

    return count


### CLASSES ###


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
        self.tree = dict()
    
    def distribute_content(self):
        pass
        
        
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
    