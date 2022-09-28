import json

from engine import render_to_string


def get_json_data():
    with open('data.json') as f:
        return json.load(f)

def main():
    template = 'index.html'
    context = {
        'title': 'Hello Caroline!',
        'posts': get_json_data()
    }
    return render_to_string(template, context)


if __name__ == '__main__':
    rendered_string = main()
