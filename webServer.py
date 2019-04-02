from http.server import HTTPServer, CGIHTTPRequestHandler


handler = CGIHTTPRequestHandler
handler.cgi_directories = ["/cgi-bin"]
httpd = HTTPServer(('10.0.0.22', 8080), handler)
httpd.serve_forever()