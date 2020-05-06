from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, request
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
import json
from typing import List

from .controller import Controller
from .api_endpoints import PROCORE_GET_USER, procore_resource_endpoint_dict, \
    PROCORE_WEBHOOKS, PROCORE_TRIGGERS, PROCORE_TRIGGER

API_VERSION = 'v2'


def fetch_token(name: str = ''):
    user = auth.current_user()
    return controller.get_token(user.email)


def update_token(token: dict, refresh_token: str = '', access_token: str = ''):
    current_user = auth.current_user()
    email = current_user and current_user.email
    if not email:
        raise Exception('User not logged in')
    
    manager = controller.get_account_manager(email)
    manager.set_procore_token(token)
    controller.update_user(manager)

    return controller.save_token(**token)


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

config_file = 'secrets/app.config'
with open(config_file, 'r') as f:
    config_contents = f.read()
config = json.loads(config_contents)
app.config.update(**config)

app.secret_key = app.config['APP_SECRET']

controller = Controller()

oauth = OAuth(app)
oauth.register('procore', fetch_token=fetch_token, 
    update_token=update_token)


@auth.verify_token
def verify_token(token):
    return controller.get_user_from_token(token)

@app.route('/')
def hello_world():
    return 'Hello world!'


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.procore.authorize_redirect(redirect_uri)


@app.route('/register')
def register():
    redirect_uri = url_for('authorize', _external=True, new_user=True)
    return oauth.procore.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    token = oauth.procore.authorize_access_token()
    procore_user = get_procore_user_from_token(token)
    user = controller.get_account_manager(procore_user.get('login'))

    if user and request.args.get('new_user'):
        return show_error('User already exists'), 403
    if not user and not request.args.get('new_user'):
        return show_error('User does not exist'), 401
    
    if user:
        user.set_procore_token(token)
        controller.update_user(user)
    else:
        controller.create_user(**procore_user, **token)

    return show_success()


def get_procore_user_from_token(token) -> dict:
    result = oauth.procore.get(PROCORE_GET_USER)
    return result.json()


@app.route('/register_webhooks', methods=['POST'])
@auth.login_required
def register_webhooks():
    hook = get_or_create_procore_webhook()
    trigger_dict = request.json
    procore_assign_triggers(hook, trigger_dict)

    return show_success()


def get_or_create_procore_webhook() -> dict:
    return get_procore_webhook() or create_procore_webhook()


def get_procore_webhook() -> dict:
    project_id = auth.current_user().project_id
    resp = oauth.procore.get(PROCORE_WEBHOOKS)
    if not resp:
        return None
    return next((h for h in resp.json() if h['owned_by_project_id'] == project_id),
        None)
    

def create_procore_webhook():
    project_id = auth.current_user().project_id
    hook_data = {
        'project_id': project_id,
        'hook': {
            'api_version': API_VERSION,
            'namespace': 'procore',
            'destination_url': url_for('webhook_handler', _external=True)
        }
    }
    return oauth.procore.post(PROCORE_WEBHOOKS, json=hook_data)


def procore_assign_triggers(hook: dict, trigger_dict: dict):
    hook_id: int = hook['id']
    project_id = auth.current_user().project_id

    existing_triggers = get_procore_existing_triggers(hook_id)
    # TODO: speed up with parallelism
    for name, is_enabled in trigger_dict.items():
        trigger_it = (t for t in existing_triggers 
            if name == t['resource_name'])
        trigger = next(trigger_it, None)

        if is_enabled and not trigger:
            create_procore_triggers(project_id=project_id,
                hook_id=hook_id, name=name)
        if not is_enabled and trigger:
            triggers_to_delete = [trigger] + list(trigger_it)
            delete_procore_triggers(triggers_to_delete)


def get_procore_existing_triggers(hook_id: int) -> List[dict]:
    uri = PROCORE_TRIGGERS.format(hook_id=hook_id)
    resp = oauth.procore.get(uri)
    return (resp and resp.json()) or []


def create_procore_triggers(project_id: str = '', hook_id: int = 0, name: str = ''):
    methods = 'create update delete'.split()
    # TODO: speed up with parallelism
    for method in methods:
        trigger_data = {
            'project_id': project_id,
            'api_version': API_VERSION,
            'trigger': {
                'resource_name': name,
                'event_type': method
            }
        }
        uri = PROCORE_TRIGGERS.format(hook_id=hook_id)
        oauth.procore.post(uri, json=trigger_data)


def delete_procore_triggers(triggers: List[dict]):
    # TODO: speed up with parallelism
    for trigger in triggers:
        uri = PROCORE_TRIGGER.format(hook_id=trigger['webhook_hook_id'], 
            trigger_id=trigger['id'])
        oauth.procore.delete(uri)


@app.route('/webhook_handler', methods=['POST'])
def webhook_handler():
    data = request.json
    try:
        dispatch_webhook(data)
        return show_success()
    except Exception as e:
        # TODO: report error to error tracker
        return show_error(str(e)), 400
    

def dispatch_webhook(data: dict):
    event_info = parse_webhook(data)

    users = controller.get_users_in_project(event_info['project_id'])
    event_object = get_procore_event_object(**event_info)
    controller.update_gcal(users, event_object)


def parse_webhook(data: dict) -> dict:
    out_dict = {}
    attrs = 'project_id resource_name resource_id'.split()
    for attr in attrs:
        value = data.get(attr)
        if not value:
            raise Exception(f'Missing {attr}')
        out_dict[attr] = value
    return out_dict


def get_procore_event_object(resource_name: str = '', resource_id: str = '',
    project_id: str = '', **kwargs) -> dict:

    endpoint = procore_resource_endpoint_dict[resource_name].format(
        project_id=project_id, resource_id=resource_id
    )

    # TODO: add user info to allow for fetching token
    resp = oauth.procore.get(endpoint)
    return resp.json()


@app.route('/test')
@auth.login_required
def test():
    company_id = auth.current_user()['company_id']
    resp = oauth.procore.get(f'/vapid/projects?company_id={company_id}')
    return resp.json()[0]


def show_success():
    return {
        'result': 'success'
    }


def show_error(error_text):
    return {
        'result': 'error',
        'error': error_text
    }
