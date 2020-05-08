from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, request, g
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
import json
from typing import List

from .api_endpoints import *
from .controller import Controller
import controller.server_connector as connector
from util.utils import parallel_for


API_VERSION = 'v2'

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
controller: Controller = None
oauth: OAuth = None

def create_app(cont):
    global app, auth, controller, oauth

    CORS(app, origins=[r'https?:\/\/[^\/]+\.procore\.com.*'])

    config_file = 'secrets/app.config'
    with open(config_file, 'r') as f:
        config_contents = f.read()
    config = json.loads(config_contents)
    app.config.update(**config)

    app.secret_key = app.config['APP_SECRET']

    controller = cont

    oauth = OAuth(app)
    oauth.register('procore', fetch_token=fetch_procore_token, 
        update_token=update_procore_token)
    oauth.register('gcal', 
        client_kwargs={'scope': 'https://www.googleapis.com/auth/calendar'})

    with app.app_context(), app.test_request_context():
        connector.url_for_webhooks = url_for('webhook_handler', _external=True)

    return app


@auth.verify_token
def verify_token(token):
    user = controller.get_user_from_token(token)
    g.user = user
    return user


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
    if not users:
        return

    g.user = users[0]
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

    resp = oauth.procore.get(endpoint)
    return resp.json()


@app.route('/test')
def test():
    rfis = controller.rfis
    lst = '\n'.join(f'<li><a href="{rfi["link"]}">{rfi["subject"]}</a></li>' 
        for rfi in rfis)
    html = f'<ul>{lst}</ul>'
    return html
    

@app.route('/gcal_login')
def gcal_login():
    redirect_uri = url_for('gcal_authorize', _external=True)
    return oauth.gcal.authorize_redirect(redirect_uri)


@app.route('/gcal_authorize')
@auth.login_required
def gcal_authorize():
    token = oauth.gcal.authorize_access_token()
    user = g.user
    user.set_gcal_token(token)
    controller.update_user(user)
    return show_success()


def show_success():
    return {
        'result': 'success'
    }


def show_error(error_text):
    return {
        'result': 'error',
        'error': error_text
    }


def fetch_procore_token(name: str = ''):
    return controller.get_token(g.user.email)


def update_procore_token(token: dict, refresh_token: str = '', access_token: str = ''):
    email = g.user and g.user.email
    if not email:
        raise Exception('User not logged in')
    
    manager = controller.get_account_manager(email)
    manager.set_procore_token(token)
    controller.update_user(manager)

    return controller.save_token(**token)

