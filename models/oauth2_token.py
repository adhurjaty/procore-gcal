class Oauth2Token:
    def __init__(self, access_token: str = '', refresh_token: str = '', token_type: str = '', 
        expires_at: int = 0, **kwargs):
        
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_at = expires_at
