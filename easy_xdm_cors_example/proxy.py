from miproxy.proxy import AsyncMitmProxy
from miproxy.proxy import RequestInterceptorPlugin
from miproxy.proxy import ResponseInterceptorPlugin

class DebugInterceptor(RequestInterceptorPlugin, ResponseInterceptorPlugin):

    def do_request(self, data):
        print repr(data)
        return data

    def do_response(self, data):
        print repr(data)
        return data

proxy = AsyncMitmProxy()
proxy.register_interceptor(DebugInterceptor)

try:
    proxy.serve_forever()
except KeyboardInterrupt:
    proxy.server_close()