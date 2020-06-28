from gevent.pywsgi import WSGIServer

from controller.request_handler import create_app


if __name__ == '__main__':
    app = create_app()
    server = WSGIServer(('', 5000), app)
    server.serve_forever()
    # app.run(host='0.0.0.0')
