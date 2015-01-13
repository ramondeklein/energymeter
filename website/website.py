#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Extend module search path
import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir, '..'))

# Import modules
from server import app
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.debug = True
app.static_folder = os.path.join(basedir, 'static-dist')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

app.run(host='0.0.0.0', port=80 if not app.debug else 8888)
