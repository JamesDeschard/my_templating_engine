import re

### CONSTANTS ###

SELF_CLOSING_TAGS = ['DOCTYPE','area', 'base', 'br', 'col', 'embed', 'hr', 'img','input', 'link', 'meta', 'param', 'source', 'track', 'wbr']


### FUNCTIONS ###

def find_specific_key(desired_key, _dict):
    """
    Find specific key in nested dictionary.
    """
    if desired_key in _dict: 
        return _dict[desired_key]
    
    for val in _dict.values():
        if isinstance(val, dict):
            result = find_specific_key(desired_key, val)
            if result is not None: 
                return result
            
    return None

def find_deepest_value(current_val):
    """
    Find deepest value in nested dictionary.
    """
    if not any([isinstance(current_val.get(k), dict) for k in current_val]):
        return current_val
    else:
        for dkey in current_val:
            if isinstance(current_val.get(dkey), dict):
                return find_deepest_value(current_val.get(dkey))
            else:
                continue


def get_html_tag_name(token):
    """
    Get the name of the HTML tag.
    """
    return re.findall(r'\w+', token.content)[0]


def get_html_attributes(token):
    """
    Get the attributes of the HTML tag (style, classes, id...).
    """
    return re.findall(r"""(\w+)=["']?((?:.(?!["']?\s+(?:\S+)=|\s*\/?[>"']))+.)["']?""", token.content)


def get_closing_expression_index(start_index, token, tokens):
    """
    Get the closing expression index.
    """
    count, new_expression = start_index + 1, 0
                    
    while not all([tokens[count].specs == 'END%s' % token.specs, new_expression <= 0]):
        if tokens[count].specs in ['FOR', 'IF']:
            new_expression += 1
        elif 'END' in tokens[count].specs:
            new_expression -= 1
        count += 1
        
    return count

def get_closing_tag_index(start_index, tag_name, tokens):   
    """
    Get the closing tag index.
    """     
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
    
