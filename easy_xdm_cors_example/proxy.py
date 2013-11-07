import contextlib
import ssl
import threading
import time
from httplib import HTTPResponse

from miproxy.proxy import MitmProxy
from miproxy.proxy import RequestInterceptorPlugin
from miproxy.proxy import ResponseInterceptorPlugin
from miproxy.proxy import ProxyHandler

class SniffingAsyncMitmProxy(MitmProxy):
    
    def __init__(self, server_address=('', 8080), RequestHandlerClass=ProxyHandler, bind_and_activate=True, ca_file='ca.pem'):
        MitmProxy.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.sniffable_content = ''
        
    def finish_request(self, request, client_address):
        proxy_handler = self.RequestHandlerClass(request, client_address, self)
        self.sniffable_content += proxy_handler.sniffable_content

class SniffingProxyHandler(ProxyHandler):
    
    def __init__(self, request, client_address, server):
        self.sniffable_content = ''
        ProxyHandler.__init__(self, request, client_address, server)
    
    def do_COMMAND(self):
        is_ssl = isinstance(self._proxy_sock, ssl.SSLSocket)  
        
        # Is this an SSL tunnel?
        if not self.is_connect:
            try:
                # Connect to destination
                self._connect_to_host()
            except Exception, e:
                self.send_error(500, str(e))
                return
            # Extract path

        # Build request
        req = '%s %s %s\r\n' % (self.command, self.path, self.request_version)
        
        self.sniffable_content += req.split('?')[0] if is_ssl else req

        if not is_ssl:
            self.sniffable_content += str(self.headers)

        # Add headers to the request
        req += '%s\r\n' % self.headers

        # Append message body if present to the request
        if 'Content-Length' in self.headers:
            body = self.rfile.read(int(self.headers['Content-Length']))
            
            if not is_ssl:
                self.sniffable_content += body
            
            req += body

        # Send it down the pipe!
        self._proxy_sock.sendall(self.mitm_request(req))

        # Parse response
        h = HTTPResponse(self._proxy_sock)
        h.begin()

        # Get rid of the pesky header
        del h.msg['Transfer-Encoding']

        # Time to relay the message across
        res = '%s %s %s\r\n' % (self.request_version, h.status, h.reason)
        
        res += '%s\r\n' % h.msg
        res += h.read()
        
        if not is_ssl:
            self.sniffable_content = res

        # Let's close off the remote end
        h.close()
        self._proxy_sock.close()

        # Relay the message
        self.request.sendall(self.mitm_response(res))

class ProxyServer(object):
    
    def __init__(self):
        self.proxy = SniffingAsyncMitmProxy(RequestHandlerClass=SniffingProxyHandler)
    
    @property
    def sniffable_content(self):
        return self.proxy.sniffable_content
    
    def start(self):
        self.server_thread = threading.Thread(target=self.proxy.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
    def shutdown(self):
        self.proxy.shutdown()
        self.server_thread.join()
    
@contextlib.contextmanager
def proxy_server():
    proxyserver = ProxyServer()
    proxyserver.start()
    
    yield proxyserver
    
    proxyserver.shutdown()
