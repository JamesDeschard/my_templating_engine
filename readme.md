# A custom templating engine made with Python

## Create a context in you main.py file

For example:

``` python
context = {
    'title': 'Hello World!',
    'posts': get_json_data()
}
```

## Create an HTML template in the index.html file

Once you have added your base markup, you can add expressions and variables to it. Similar to twig or jinja

### Expressions

You can use {% %} tags to add forloops or conditions 

For example:

``` html
{% if title %}
    <h1 class="title" style="color:red;">{{title}}</h1>
{% endif %}
```

or 

``` html
 {% for post in posts %}

    <p>This markup will be added for each post in the posts variable!</p>

{% endfor %}
```

### Variables

You can use {{ }} tags to add a variable

For example:

``` html
<h2>{{post.title}}</h2>
<p>{{post.body}}</p>
```

## Call the render_to_string() method to create your new HTML template

The render_to_string method takes two parameters, the previously defined context and the name of your html file. The html file must be in the root of your working directory.
Like so:

``` python
return render_to_string(template, context)
```


## Parse the HTML

You can also use this piece of software as a parser for your HTML. This will represent your document file in the form of a navigable AST.
