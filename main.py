import json

from engine.engine import render_to_string


def get_json_data():
    with open('data.json') as f:
        return json.load(f)

def main():
    template = 'index.html'
    context = {
        'title': 'forloop',
        'test': {'name': 'James', 'age': 20, 'surname': 'Bond'},
        'posts': get_json_data(),
        'name': 'Bob',
        'age': 20
    }
    return render_to_string(template, context)


if __name__ == '__main__':
    rendered_string = main()
