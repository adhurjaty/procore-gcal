from .procore_view_model import ProcoreViewModel
from .web_view_model import WebViewModel
from .gcal_view_model import GCalViewModel
from interactor.account_manager_response import AccountManagerResponse
from interactor.user_response import UserResponse


class VMFactory:
    def create_procore_vm(self, user: AccountManagerResponse) -> ProcoreViewModel:
        return ProcoreViewModel(user)

    def create_web_vm(self) -> WebViewModel:
        return WebViewModel()

    def create_gcal_vm(self, user: UserResponse) -> GCalViewModel:
        return GCalViewModel(user)
