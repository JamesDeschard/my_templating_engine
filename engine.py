import codecs

class Lexer:
    left_brace = 'EXPRESSION_START'
    right_brace = 'EXPRESSION_END'
    

    def __init__(self, template) -> None:
        self.template = template
        self.tokens = []
        
    def tokenize(self):
        for index, char in enumerate(self.template):
            print(char)
            if char == '{':
                if self.template[index + 1] in ['{%']:
                    if self.template[index + 2] == '%':
                        self.tokens.append((self.left_brace))
            elif char == '}':
                if self.template[index + 1] in ['%}']:
                    if self.template[index + 2] == '}':
                        self.tokens.append((self.left_brace))
                
        return self.tokens
    
class Engine:
    
    def __init__(self, template, data) -> None:
        self.template = codecs.open(template, 'r', 'utf-8').read()
        self.data = data
        
        print(Lexer(self.template).tokenize())
        
        
    