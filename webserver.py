#!/usr/bin/python
from log import initialize_logging, logging

if __name__ == "__main__":
    # Obtain the name of the logfile
    initialize_logging('webserver')

    # Setup logger
    logger = logging.getLogger(__name__)

    from flask import Flask
    app = Flask(__name__)

    import os
    from config import configuration

    # Extend module search path
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Import modules
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.debug = True
    app.static_folder = os.path.join(basedir, 'website/static-dist')

    # Import modules
    from api import init_api
    from static import init_static

    # Initialize modules
    init_api(app)
    init_static(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    # Obtain hostname and port number
    hostname = configuration.get('webserver', 'hostname') if configuration.has_option('webserver', 'hostname') else '0.0.0.0'
    port = configuration.getint('webserver', 'port') if configuration.has_option('webserver', 'port') else 80
    app.run(host=hostname, port=port)
