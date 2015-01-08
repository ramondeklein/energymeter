#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Extend module search path
import sys
sys.path.append('..')

# Import modules
from helpers import Database, Settings
from os import curdir
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

def sanitize(path):
  # TODO: Implement URL sanitazation
  if path == '/':
    path = '/index.html'
  return path

class MyHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    try:
      # Obtain the request path
      path = sanitize(self.path)
      if not path.startswith('/api'):
        f = open('{}/content/{}'.format(curdir, path))
        self.send_response(200)
        content_type = 'application/octet-stream'
	if path.endswith('.html'):
          content_type = 'text/html'
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(f.read())
        f.close()
      else:
        self.send_error(404, 'API not implemented yet.')
    except IOError:
      self.send_error(404, 'Path {} not found'.format(self.path))
    except Exception as exc:
      logger.error("Exception: {}".format(exc))
      self.send_error(500, 'Exception caught (check server logging)')

port = 8888
server = None
try:
  server = HTTPServer(('', port), MyHandler)
  print 'Listening on port {}...'.format(port)
  server.serve_forever()
except KeyboardInterrupt:
  print ' received'
finally:
  print 'Shutting down...'
  server.socket.close()
