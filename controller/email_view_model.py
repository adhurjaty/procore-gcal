from interactor.account_manager_response import AccountManagerResponse
from util.utils import get_config


config = get_config()


class EmailViewModel:
    user: AccountManagerResponse = None

    def __init__(self, user: AccountManagerResponse):
        self.user = user

    def signup_email(self):
        return {
            'full_name': self.user.full_name,
            'link': config.get('FRONT_END_DOMAIN'),
            'subject': 'Welcome to Procore Calendar Integrator'
        }

    def delete_user_email(self, user: AccountManagerResponse):
        pass

