#!/usr/bin/python

# Setup logging
import logging
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)

# Extend module search path
import os, sys
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir, '..'))

# Import modules
from app import app
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.static_folder = os.path.join(basedir, 'static')
app.run(host='0.0.0.0', port=8888, debug=True)
