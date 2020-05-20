import abc

class PresenterInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_user_info(self, token):
        raise NotImplementedError