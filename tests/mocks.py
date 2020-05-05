class MockObject:
    def __init__(self):
        pass
    

class OauthMock:
    token = {}
    redirect_uri = ''

    def authorize_redirect(self, uri: str):
        self.redirect_uri = uri

    def authorize_access_token(self) -> dict:
        return token

    def set_token(self, token: dict):
        self.token = token

    