from .web_view_model import WebViewModel
from interactor.presenter_interface import PresenterInterface
from interactor.account_manager_response import AccountManagerResponse

class Presenter(PresenterInterface):
    def get_user_info(self, token):
        raise NotImplementedError

    def get_manager_vm(self, user: AccountManagerResponse) -> dict:
        vm = WebViewModel()
        return vm.show_user(user)