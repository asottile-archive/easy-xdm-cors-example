import argparse
import flask
import os.path
from OpenSSL import SSL


app = flask.Flask(__name__)

APP_ROOT = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def index():
    return APP_ROOT
    return 'Hello World'

EXTENSIONS_TO_MIMETYPES = {
    '.js': 'application/javascript',
    '.html': 'text/html',
}

STATIC_DIR = 'static'

EXTENSIONS_TO_STATIC_DIRS = {
    '.js': 'static/js',
    '.html': 'static/html',
}

assert set(EXTENSIONS_TO_MIMETYPES.keys()) == set(EXTENSIONS_TO_STATIC_DIRS.keys())

@app.route('/<path:path>')
def catch_all(path):
    if not app.debug:
        flask.abort(404)

    if not any(
        path.endswith(extension)
        for extension in EXTENSIONS_TO_MIMETYPES.keys()
    ):
        flask.abort(404)

    extension = os.path.splitext(path)[1]

    try:
        file_path = os.path.join(
            APP_ROOT,
            EXTENSIONS_TO_STATIC_DIRS[extension],
            path,
        )

        if not file_path.startswith(os.path.join(APP_ROOT, STATIC_DIR)):
            flask.abort(404)

        with open(file_path) as asset_file:
            return flask.Response(
                 asset_file.read(),
                 mimetype=EXTENSIONS_TO_MIMETYPES[extension],
            )
    except IOError:
        flask.abort(404)

def is_ssl():
    parser = argparse.ArgumentParser(description="Start easy-xdm server")
    parser.add_argument('--ssl', type=bool, required=False, default=False)
    args = parser.parse_args()

    return args.ssl


if __name__ == '__main__':
    context = None
    port = None
    if is_ssl():
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file('cert/server.key')
        context.use_certificate_file('cert/server.crt')
        port = 9001

    app.run(debug=True, ssl_context=context, port=port)
