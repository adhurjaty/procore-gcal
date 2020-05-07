from authlib.integrations.requests_client import OAuth2Session
from .api_endpoints import *


API_VERSION = 'v2'


class ProcoreViewModel:
    def __init__(self, user, ):
        super().__init__()
    oauth: OAuth2Session = None
    

class ProcoreHook:
    def __init__(self, project_id: str, dest_url: str):
        self.project_id = project_id
        self.destination_url: dest_url

    def to_dict(self):
        return {
            'project_id': self.project_id,
            'hook': {
                'api_version': API_VERSION,
                'namespace': 'procore',
                'destination_url': self.destination_url
            }
        }


class ProcoreEvent:
    def __init__(self, hook: ProcoreHook = None, resource_name: str = '',
        event_type: str = ''):
        
        self.hook = hook
        self.resource_name = resource_name
        self.event_type = event_type
    
    def to_dict(self):
        return {
            'project_id': self.hook.project_id,
            'api_version': API_VERSION,
            'trigger': {
                'resource_name': self.resource_name,
                'event_type': self.event_type
            }
        }
    