def init_static(app):
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def static_proxy(path):
        return app.send_static_file(path)
