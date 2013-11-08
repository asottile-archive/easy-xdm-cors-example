import argparse
import flask
import mako.lookup
import OpenSSL.SSL
import os.path
import simplejson

from util.decorators import require_secure

app = flask.Flask(__name__)

HTTP_PORT = 5000
SSL_PORT = 9001

template_lookup = mako.lookup.TemplateLookup(
    directories=['easy_xdm_cors_example/templates'],
)

APP_ROOT = os.path.abspath(os.path.dirname(__file__))

def render_template(template_name, **env):
    template = template_lookup.get_template(template_name)
    return template.render(**env)

@app.route('/')
def index():
    host = flask.request.host.split(':')[0]
    return render_template('index.mako', host=host, ssl_port=SSL_PORT)

def get_cross_origin_response(form={}):
    response = flask.Response(
        simplejson.dumps({
            'original_request': form,
            'success': True,
        }),
        mimetype='application/json',
    )
    response.headers['Access-Control-Allow-Origin'] = 'http://{0}:{1}'.format(
        flask.request.host.split(':')[0],
        HTTP_PORT,
    )
    return response

@app.route('/post_endpoint', methods=['POST'])
@require_secure
def secure_post_endpoint():
    return get_cross_origin_response(flask.request.form)

@app.route('/get_endpoint', methods=['GET'])
@require_secure
def secure_get_endpoint():
    return get_cross_origin_response()

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
    parser.add_argument('--ssl', action='store_true', required=False, default=False)
    args = parser.parse_args()

    return args.ssl

if __name__ == '__main__':
    port = HTTP_PORT
    context = None

    if is_ssl():
        port = SSL_PORT
        context = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
        context.use_privatekey_file('cert/server.key')
        context.use_certificate_file('cert/server.crt')

    app.run('0.0.0.0', port, debug=True, use_reloader=False, ssl_context=context)
