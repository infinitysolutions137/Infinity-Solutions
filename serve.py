import http.server

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        # Force fresh 200 response by removing client cache headers
        if 'if-modified-since' in self.headers:
            del self.headers['if-modified-since']
        if 'if-none-match' in self.headers:
            del self.headers['if-none-match']
        return super().send_head()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    http.server.test(HandlerClass=NoCacheHTTPRequestHandler, port=3000)
