from .procore_view_model import ProcoreViewModel
from .web_view_model import WebViewModel
from interactor.user_response import UserResponse


class VMFactory:
    def create_procore_vm(self, user: UserResponse) -> ProcoreViewModel:
        return ProcoreViewModel(user)

    def create_web_vm(self):
        return WebViewModel()
