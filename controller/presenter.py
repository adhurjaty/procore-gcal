from .web_view_model import WebViewModel
from interactor.presenter_interface import PresenterInterface
from interactor.account_manager_response import AccountManagerResponse
from interactor.user_response import UserResponse

class Presenter(PresenterInterface):
    def get_user_info(self, token):
        raise NotImplementedError

    def get_manager_vm(self, user: AccountManagerResponse) -> dict:
        vm = WebViewModel()
        return vm.show_user(user)

    def get_event(self, user: UserResponse, resource_name: str='', resource_id: int=-1):
        raise NotImplementedError

    def update_gcal(self, user: AccountManagerResponse, event: ProcoreEvent):
        raise NotImplementedError