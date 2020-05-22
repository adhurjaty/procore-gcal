from .gcal_view_model import GCalViewModel
from .procore_view_model import ProcoreViewModel
from .web_view_model import WebViewModel
from interactor.presenter_interface import PresenterInterface
from interactor.account_manager_response import AccountManagerResponse
from interactor.user_response import UserResponse
from interactor.procore_event import ProcoreEvent

class Presenter(PresenterInterface):
    def get_user_info(self, token):
        raise NotImplementedError

    def get_manager_vm(self, user: AccountManagerResponse) -> dict:
        vm = WebViewModel()
        return vm.show_user(user)

    def get_procore_event(self, user: UserResponse, resource_name: str='', 
        resource_id: int=-1) -> ProcoreEvent:

        vm = ProcoreViewModel(user)
        event = vm.get_event(resource_name=resource_name, resource_id=resource_id)
        procore_event = ProcoreEvent()
        procore_event.update_from_dict(event)
        return procore_event

    def update_gcal(self, user: AccountManagerResponse, event: ProcoreEvent):
        raise NotImplementedError