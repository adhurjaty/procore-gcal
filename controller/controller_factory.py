from controller.controller import Controller
from controller.presenter import Presenter
from controller.vm_factory import VMFactory
from interactor.use_case_interactor import UseCaseInteracor
from models.db_interface import DBInterface

class ControllerFactory:
    @staticmethod
    def create():
        vm_factory = VMFactory()
        presenter = Presenter(vm_factory)
        db_int = DBInterface()
        interactor = UseCaseInteracor(presenter, db_int)
        return Controller(interactor)