from controller.request_handler import create_app
from controller.controller import Controller
from controller.presenter import Presenter
from controller.vm_factory import VMFactory
from interactor.use_case_interactor import UseCaseInteracor
from models.db_interface import DBInterface


if __name__ == '__main__':
    vm_factory = VMFactory()
    presenter = Presenter(vm_factory)
    db_int = DBInterface()
    interactor = UseCaseInteracor(presenter, db_int)
    controller = Controller()
    app = create_app(controller)
    app.run(host='0.0.0.0')
