# A custom templating engine made with Python

Because the ``replace`` and ``format`` methods are too easy...

## How does it work?

This project has two main components, a small programming language (evaluate.py) and a templating engine (engine.py). The language is designed to evaluate expressions passed to the templating engine expression tags. For instance to evaluate ``{% if 10+10 * (4/2) == 10 %}`` we will pass this expression to the ``evaluate`` method of the evaluate.py file and will receive a ``True``or ``False`` result. Using ``eval()`` would just be cheating... and dangerous!

### The Lexer

The lexer just turns a meaningless string into a flat list of things like "number literal", "string literal", "identifier", or "operator", and can do things like recognizing reserved identifiers ("keywords") and discarding whitespace.

- *The evaluate.py Lexer*: This Lexer traverses a string and replaces various operators, terms or factors by the appropriate Token. For example let's take the expression: `(2*5) + 2`. Once it has been "tokenized", it will look like this: `[LPAREN, INTEGER:2, MUL, INTEGER:5, RPAREN, PLUS, INTEGER:2]`

- *The engine.py Lexer*: Same logic here put the tokens represent HTML tags, variables of expressions. For example let's take the expression: `<h1>{{ name }}</h1>`. Once it has been "tokenized", it will look like this: `[TAG:<h1>:0, VARIABLE: name :5, TAG:</h1>:14]`

### The Parser
The parser has the much harder job of turning the stream of "tokens" produced by the lexer into a parse tree representing the structure of the parsed language.

- *The evaluate.py Parser*: This parser is an implementation of the shunting yard algorithm. It transforms our tokens into a more readable version of the demanded expression.
Let's continue our `(2*5) + 2` example. Once it has been parsed, it will look like this: `((2, MUL, 5), PLUS, 2)`

- *The engine.py Parser*: I must confess that the design of this algorithm was done by yours truly so it might not be the most optimized of things! The idea remains the same. We are decomposing our HTML file into an AST. Let's continue our `<h1>{{ name }}</h1>` example. Once it has been parsed, it will look like this: `{h1: { name : {}}}`. So we transformed our HTML into a nested python dictionnary.

### The Interpreter
An interpreter is a computer program that is used to directly execute program instructions written using one of the many high-level programming languages.

- *The evaluate.py Interpreter*: The final stage of the process. The parsed expression is computed and turned into the wanted output. In our example the interpreter will return `12`.

- *The engine.py Interpreter*: With the engine, the job of the interpreter is to recursively traverse the nested dictionary and populate it with the various content of the HTML tags. Our result value for our previous example will therefore be `<h1>James</h1>` (assuming our variable matches to the string "James", more on that later).

## Create a context 

The context is a dictionnary containing the data you want to integrate in your HTML document.

``` python
context = {
    'title': 'Hello World!',
    'name': 'James'
    'posts': get_json_data()
}
```

## Create an HTML template

Templates are to be added to the templates directory.
Once you have added your boilerplate markup, you can add expressions and variables from your context into it.

### Variables

You can use ``{{ }}`` tags to add a variable.

``` html
<h1>{{ value }}</h1>
```

Variables can also be nested

``` html
<h1>{{ values.value }}</h1>
<h2>{{ values.value.first }}<H2>
<h3>{{ values.value.first.second }}<h3>
...
```

### Expressions

Two types of expressions are currently supported, for loops and if statements. You can cumulate conditions with the `else` and `else` tags.
You can use ``{% %}`` tags to add forloops or conditions. Expressions start with an ``if`` or ``for`` tag and end with an ``endif`` or ``endfor`` tag. You can obviously integrate variables to expressions.

For example:

``` html
{% if title %}
    ...
{% elif person.name %}
    ...
{% else %}
    ...
{% endif %}
```

or 

``` html
{% for post in posts %}
    <h1>{{ post.title }}</h1>
    <p>{{post.body}}</p>
{% endfor %}
```

## Call the render_to_string() method to create your new HTML template
 
To add data to a template, call the render_to_string method. It takes two parameters, the previously defined context and the name of your html file.
For example:

``` python
def main():
    template = 'index.html'
    context = {
        'title': 'Hello World !',
    }
    return render_to_string(template, context)
```