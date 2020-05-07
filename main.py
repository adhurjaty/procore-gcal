from controller.request_handler import create_app, stop_app
from controller.controller import Controller


if __name__ == '__main__':
    controller = Controller()
    app = create_app(controller)
    app.run(host='0.0.0.0')
