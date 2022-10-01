import copy
import re
import os



### CONSTANTS ###

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATHEMATICAL_OPERATORS = ['+','-','*','^','.','/','(',')']
LOGICAL_OPERATORS = ['==', '!=', '>', '<', '>=', '<=', 'and', 'or', 'not']
SELF_CLOSING_TAGS = ['DOCTYPE','area', 'base', 'br', 'col', 'embed', 'hr', 'img','input', 'link', 'meta', 'param', 'source', 'track', 'wbr']


### FUNCTIONS ###

def add_tabulation_and_line_breaks(_string, tabulation=0):
    """
    Returns a string with tabulations and line breaks.
    """
    return '\n' + '  ' * tabulation + _string

def depth(_dict):
    """
    Returns a list of the depth of each key in a nested dictionary.
    """
    depth = []
    stack = [(_dict, list(_dict.keys()))]
    while stack:
        cur, keys = stack.pop()
        while keys:
            k, keys = keys[0], keys[1:]
            depth.append((k, len(stack) + 1))
            v = cur[k]
            if isinstance(v, dict):
                stack.append((cur, keys))
                stack.append((v, list(v.keys())))
                break
    return dict(depth)


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


class RetrieveVarsFromExpression:
    """
    Gets the value of a variable from the context.
    Works with simple as well as nested variables.
    If a variable is a mathematical expression or a string 
    it is left untouched.
    
    Returns the full expression, ready to be evaluated.
    """
    def __init__(self, expression_type, expression, context) -> None:
        self.expression_type = expression_type
        self.expression = expression
        self.context = context
        self.existing_vars = []
        
        self.assumed_vars = expression.split()

    def manager(self):
        if self.expression_type == 'for':
            existing_variables = list(map(self.retrieve, self.assumed_vars))[0]
            return existing_variables
        
        elif self.expression_type == 'if':
            existing_variables = map(self.retrieve, self.assumed_vars)
            existing_variables = filter(lambda x: x != None, existing_variables)
            new_expression = self.build_expression_for_evaluation(existing_variables)
            return new_expression
        
        else:
            return list(map(self.retrieve, self.assumed_vars))[0]
    
    def build_expression_for_evaluation(self, existing_variables):
        expression_terms = self.expression.split()
        operator_indexes = [expression_terms.index(x) for x in expression_terms if x in LOGICAL_OPERATORS]

        fill_operator_indexes = []
        for index, var_name in enumerate(existing_variables):
            if not self.is_string(var_name) and not self.is_mathematical_expression(var_name):
                var_name = f'"{var_name}"'
            if index in operator_indexes:
                fill_operator_indexes.append('')
                
            fill_operator_indexes.append(var_name)
    
        var_names_and_operators = zip(expression_terms, fill_operator_indexes)
        new_expression = map(lambda x: x[1] if x[1] != '' else x[0], var_names_and_operators)
        new_expression = ' '.join(new_expression)
        return new_expression    

    def get_variable_from_context(self, variable, context):
        variable = context.get(variable, False)
        
        if type(variable) == int:
            variable = str(variable) 
        
        return variable
    
    def is_mathematical_expression(self, var):
        return all([v in MATHEMATICAL_OPERATORS or v.isdigit() for v in var])
    
    def is_string(self, var):
        return all([var.startswith('"'), var.endswith('"')]) 
    
    def retrieve(self, var):
        if self.is_string(var):
            return var
        elif self.is_mathematical_expression(var):
            return var
        elif var in LOGICAL_OPERATORS:
            return None
        
        current_var = var.split('.')
                
        if len(current_var) == 1:
            variable = self.get_variable_from_context(current_var[0], self.context)
            return variable

        else:
            count = 0
            variable = copy.deepcopy(self.context)
            while count != len(current_var):
                variable = self.get_variable_from_context(current_var[count], variable)
                count += 1
                
        return variable
        