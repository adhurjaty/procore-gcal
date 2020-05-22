import abc

from .account_manager_response import AccountManagerResponse

class PresenterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_user_info(self, token):
        raise NotImplementedError

    @abc.abstractmethod
    def get_manager_vm(self, user: AccountManagerResponse) -> dict:
        raise NotImplementedError