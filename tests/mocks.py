from interactor.account_manager_dto import AccountManagerDto
from models.account_manager import AccountManager

class MockObject:
    def __init__(self):
        pass


class OauthMock:
    token = {}
    redirect_uri = ''

    def authorize_redirect(self, uri: str):
        self.redirect_uri = uri

    def authorize_access_token(self) -> dict:
        return self.token

    def set_token(self, token: dict):
        self.token = token

    
class OauthResponseMock:
    status_code = 200
    
    def __init__(self, response):
        self.response = response
    
    def json(self):
        return self.response


class ControllerMock:
    manager = None

    def __init__(self, *args, **kwargs):
        pass

    def get_account_manager(self, login: str):
        if self.manager and self.manager.email == login:
            return self.manager
        return None

    def set_manager(self, manager):
        self.manager = manager

    def update_user(self, user):
        pass

    def create_user(self, login: str = '', name: str = '', **token):
        self.manager = AccountManagerDto(AccountManager)
        self.manager.email = login
        self.manager.full_name = name
        self.manager.set_procore_token(token)
    
    def get_user_from_token(self, _):
        return self.manager