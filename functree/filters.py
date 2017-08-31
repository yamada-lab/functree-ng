import base64
from functree import app


def b64decode(string):
    return base64.b64decode(string).decode('utf-8')


app.jinja_env.filters['b64decode'] = b64decode
