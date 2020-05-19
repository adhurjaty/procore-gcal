from authlib.integrations.requests_client import OAuth2Session
from typing import List

from .api_endpoints import *
from .server_connector import url_for_webhooks
from interactor.account_manager_dto import AccountManagerDto
from util.utils import parallel_for


API_VERSION = 'v2'


class ProcoreHook:
    def __init__(self, id: int = 0, project_id: str = '', destination_url: str = '',
        owned_by_project_id: str = '', **kwargs):

        self.id = id
        self.project_id = project_id or owned_by_project_id
        self.destination_url = destination_url or url_for_webhooks

    def to_create_dict(self) -> dict:
        return {
            'project_id': self.project_id,
            'hook': {
                'api_version': API_VERSION,
                'namespace': 'procore',
                'destination_url': self.destination_url
            }
        }


class ProcoreTrigger:
    def __init__(self, hook: ProcoreHook = None, id: int = 0, webhook_hook_id: int = 0,
        resource_name: str = '', resource_id: int = 0, event_type: str = '',
        project_id: str = '', **kwargs):
        
        self.id = id
        self.hook_id = webhook_hook_id or (hook and hook.id)
        self.project_id = project_id or (hook and hook.project_id)
        self.resource_name = resource_name
        self.resource_id = resource_id
        self.event_type = event_type
    
    def to_create_dict(self):
        return {
            'project_id': self.project_id,
            'api_version': API_VERSION,
            'trigger': {
                'resource_name': self.resource_name,
                'event_type': self.event_type
            }
        }
    

class ProcoreViewModel:
    def __init__(self, user: AccountManagerDto = None, token: dict = None):
        if user:
            self.oauth = OAuth2Session(token=user.procore_data.access_token,
                update_token=self._update_token)
            self.user = user
        elif token:
            self.oauth = OAuth2Session(token=token)

    def _update_token(self, token):
        self.user.set_procore_token(token)

    def register_webhooks(self):
        hook = self._get_or_create_procore_webhook()
        trigger_dict = self.user.procore_data.calendar_event_types
        self._procore_assign_triggers(hook, trigger_dict)

    def _get_or_create_procore_webhook(self) -> dict:
        return self._get_procore_webhook() or self._create_procore_webhook()

    def _get_procore_webhook(self) -> ProcoreHook:
        project_id = self.user.project_id
        resp = self.oauth.get(PROCORE_WEBHOOKS)
        hooks = (resp and resp.json()) or []
        return next((ProcoreHook(**h) for h in resp.json() 
            if h['owned_by_project_id'] == project_id), None)
        
    def _create_procore_webhook(self) -> ProcoreHook:
        hook = ProcoreHook(project_id=self.user.project_id)
        resp = self.oauth.post(PROCORE_WEBHOOKS, json=hook.to_create_dict())
        created_hook = ProcoreHook(**resp)
        return created_hook

    def _procore_assign_triggers(self, hook: ProcoreHook, trigger_dict: dict):
        project_id = self.user.project_id

        existing_triggers = self._get_procore_existing_triggers(hook)
        def create_or_delete_triggers(item):
            name, is_enabled = item
            trigger_it = (t for t in existing_triggers 
                if name == t.resource_name)
            trigger = next(trigger_it, None)

            if is_enabled and not trigger:
                self._create_procore_triggers(hook=hook, name=name)
            if not is_enabled and trigger:
                triggers_to_delete = [trigger] + list(trigger_it)
                self._delete_procore_triggers(triggers_to_delete)

        parallel_for(create_or_delete_triggers, trigger_dict.items())

    def _get_procore_existing_triggers(self, hook: ProcoreHook) -> List[ProcoreTrigger]:
        uri = PROCORE_TRIGGERS.format(hook_id=hook.id)
        resp = self.oauth.get(uri)
        triggers = (resp and resp.json()) or []
        return [ProcoreTrigger(**trigger) for trigger in triggers]

    def _create_procore_triggers(self, hook: ProcoreHook = None, name: str = ''):
        methods = 'create update delete'.split()
        def create_trigger(method):
            trigger = ProcoreTrigger(hook, resource_name=name, event_type=method)
            uri = PROCORE_TRIGGERS.format(hook_id=trigger.hook_id)
            self.oauth.post(uri, json=trigger.to_create_dict())

        parallel_for(create_trigger, methods)

    def _delete_procore_triggers(self, triggers: List[ProcoreTrigger]):
        def delete_trigger(trigger):
            uri = PROCORE_TRIGGER.format(hook_id=trigger.hook_id, 
                trigger_id=trigger.id)
            self.oauth.delete(uri)

        parallel_for(delete_trigger, triggers)

    def get_user_info(self):
        user_resp = self.oauth.get(PROCORE_GET_USER)
        if user_resp.status_code != 200:
            return None
        
        # TODO: get project info

        return user_resp.json()
        