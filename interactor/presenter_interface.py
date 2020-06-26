import abc

from .account_manager_response import AccountManagerResponse
from .user_response import UserResponse
from .procore_event import ProcoreEvent

class PresenterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_user_info(self, token: dict) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def get_manager_vm(self, user: AccountManagerResponse) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def get_procore_event(self, user: UserResponse, resource_name: str='', resource_id: int=-1):
        raise NotImplementedError

    @abc.abstractmethod
    def update_gcal(self, user: AccountManagerResponse, event: ProcoreEvent):
        raise NotImplementedError

    @abc.abstractmethod
    def set_manager_selections(self, user: AccountManagerResponse):
        raise NotImplementedError

    @abc.abstractmethod
    def update_webhook_triggers(self, user: AccountManagerResponse):
        raise NotImplementedError