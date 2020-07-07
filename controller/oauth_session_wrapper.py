from authlib.integrations.requests_client import OAuth2Session
import os
import json
from pathlib import Path
from util.utils import get_config


class OauthSessionWrapper:
    oauth: OAuth2Session = None
    base_url: str = ''

    def __init__(self, config_prefix: str, token: dict = {}, update_token=None):
        oauth_settings = self._get_oauth_settings(config_prefix)
        self.base_url = oauth_settings.get('base_url')
        self.oauth = OAuth2Session(**oauth_settings, token=token, update_token=update_token)

    def _get_oauth_settings(self, config_prefix: str) -> dict:
        oauth_settings = get_config()
        prefix = config_prefix.upper()
        return {
            'client_id': oauth_settings.get(f'{prefix}_CLIENT_ID'),
            'client_secret': oauth_settings.get(f'{prefix}_CLIENT_SECRET'),
            'authorization_endpoint': oauth_settings.get(f'{prefix}_AUTHORIZE_URL'),
            'token_endpoint': oauth_settings.get(f'{prefix}_ACCESS_TOKEN_URL'),
            'base_url': oauth_settings.get(f'{prefix}_API_BASE_URL')
        }

    def get(self, endpoint, **kwargs):
        return self.oauth.get(self._full_url(endpoint), **kwargs)

    def post(self, endpoint, **kwargs):
        return self.oauth.post(self._full_url(endpoint), **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.oauth.delete(self._full_url(endpoint), **kwargs)

    def patch(self, endpoint, **kwargs):
        return self.oauth.patch(self._full_url(endpoint), **kwargs)

    def put(self, endpoint, **kwargs):
        return self.oauth.put(self._full_url(endpoint), **kwargs)

    def _full_url(self, endpoint):
        return f'{self.base_url}{endpoint}'
