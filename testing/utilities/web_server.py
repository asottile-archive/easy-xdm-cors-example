
from easy_xdm_cors_example.app import get_http_server
from testing.utilities.background_context import BackgroundContext

class WebServer(BackgroundContext):

    def __init__(self, is_ssl):
        super(WebServer, self).__init__()
        self.server = get_http_server(is_ssl)

    def background_action(self):
        self.server.serve_forever()

    def teardown(self):
        self.server.shutdown()
