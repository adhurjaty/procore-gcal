from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, request, g, redirect, make_response
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
import json
from typing import List

from .api_endpoints import *
from .controller import Controller
import controller.server_connector as connector
from util.utils import parallel_for, build_url


API_VERSION = 'v2'

INDEX_ROUTE = '/api'
LOGIN_ROUTE = '/login'
REGISTER_ROUTE = '/api/register'
PROCORE_AUTH_ROUTE = '/authorize'
WEBHOOK_HANDLER_ROUTE = '/api/webhook_handler'
GCAL_LOGIN_ROUTE = '/gcal_login'
GCAL_COLLABORATOR_LOGIN_ROUTE = '/gcal_login_collab/<collaborator_id>'
GCAL_AUTH_ROUTE = '/gcal_authorize'
USER_ROUTE = '/api/users/<user_id>'


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
controller: Controller = None
oauth: OAuth = None

def create_app(cont: Controller) -> Flask:
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
    oauth.register('procore', fetch_token=_fetch_procore_token, 
        update_token=_update_procore_token)
    oauth.register('gcal', 
        client_kwargs={'scope': 'https://www.googleapis.com/auth/calendar'})

    # HACK: don't really like having to set this here
    with app.app_context(), app.test_request_context():
        connector.url_for_webhooks = url_for('webhook_handler', _external=True)

    return app


@auth.verify_token
def verify_token(token):
    user = controller.get_user_from_token(token)
    if not user:
        return None
    g.user = user
    return user


@app.route(INDEX_ROUTE)
def hello_world():
    return 'Hello world!'


@app.route(LOGIN_ROUTE)
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.procore.authorize_redirect(redirect_uri)

@app.route(PROCORE_AUTH_ROUTE)
def authorize():
    token = oauth.procore.authorize_access_token()
    user = controller.get_user_from_token(token.get('access_token'))

    try: 
        if user:
            user.set_procore_token(token)
            controller.update_user(user)
        else:
            user = controller.init_user(token)

        return _redirect_to_manager_page(user, token.get('access_token'))
    except Exception as e:
        return _show_error(str(e))


def _get_procore_user_from_token(token) -> dict:
    result = oauth.procore.get(PROCORE_GET_USER)
    user = result and result.json()
    if not user or 'login' not in user or 'name' not in user:
        return None
    return result.json()


def _redirect_to_manager_page(user, procore_token=None):
    path = '/users/' + (str(user.id) if user and user.id else 'new')
    return _redirect_to_user_page(path, user, procore_token)

    
def _redirect_to_user_page(path, user, procore_token=None):
    param_dict = {} if user and user.id else {'fullName': user.full_name, 'email': user.email}
    redirect_url = build_url(app.config.get("FRONT_END_DOMAIN"), path, param_dict)    
    
    response = make_response(redirect(redirect_url))
    if(procore_token):
        response.set_cookie('auth_token', procore_token)
    return response
    

@app.route(WEBHOOK_HANDLER_ROUTE, methods=['POST'])
def webhook_handler():
    data = request.json
    try:
        _dispatch_webhook(data)
        return _show_success()
    except Exception as e:
        # TODO: report error to error tracker
        return _show_error(str(e))
    

def _dispatch_webhook(data: dict):
    event_info = _parse_webhook(data)
    controller.update_gcal(**event_info)

    users = controller.get_users_in_project(event_info['project_id'])
    if not users:
        return

    g.user = users[0]
    event_object = _get_procore_event_object(**event_info)
    controller.update_gcal(users, event_info.get('resource_name'), event_object)


def _parse_webhook(data: dict) -> dict:
    out_dict = {}
    attrs = 'project_id resource_name resource_id'.split()
    for attr in attrs:
        value = data.get(attr)
        if not value:
            raise Exception(f'Missing {attr}')
        out_dict[attr] = value
    return out_dict


def _get_procore_event_object(resource_name: str = '', resource_id: str = '',
    project_id: str = '', **kwargs) -> dict:

    endpoint = procore_resource_endpoint_dict[resource_name].format(
        project_id=project_id, resource_id=resource_id
    )

    resp = oauth.procore.get(endpoint)
    return resp.json()


@app.route(GCAL_LOGIN_ROUTE)
@auth.login_required
def gcal_login():
    auth_token = g.user.procore_data.access_token

    redirect_uri = url_for('gcal_authorize', _external=True, auth_token=auth_token)
    return oauth.gcal.authorize_redirect(redirect_uri)


@app.route(GCAL_COLLABORATOR_LOGIN_ROUTE)
def gcal_collaborator_login(collaborator_id):
    redirect_uri = url_for('gcal_authorize', _external=True, collaborator=collaborator_id)
    return oauth.gcal.authorize_redirect(redirect_uri)


@app.route(GCAL_AUTH_ROUTE)
def gcal_authorize():
    gcal_token = oauth.gcal.authorize_access_token()
    auth_token = request.args.get('auth_token')

    try:
        # if this is an account manager update
        if auth_token:
            user = _update_user_gcal_token(auth_token, gcal_token)
            return _redirect_to_manager_page(user)
        else:
            collaborator = _update_collaborator_gcal_token(gcal_token)
            return _redirect_to_collaborator_page(collaborator)
        
    except Exception as e:
        return _show_error(str(e))


def _update_user_gcal_token(auth_token, gcal_token):
    user = controller.get_user_from_token(auth_token)
    if not user:
        raise Exception('Invalid authorization token')
    user.set_gcal_token(gcal_token)
    controller.update_user(user)
    return user


def _update_collaborator_gcal_token(token):
    collaborator_id = request.args.get('collaborator_id')
    if not collaborator_id:
        raise Exception('Malformed redirect URL')

    collaborator = controller.get_collaborator(collaborator_id)
    collaborator.set_gcal_token(token)
    controller.update_user(collaborator)
    return collaborator


def _redirect_to_collaborator_page(collaborator):
    path = f'/collaborators/{collaborator.id}'
    return _redirect_to_user_page(path, collaborator)


@app.route(USER_ROUTE, methods=['PATCH'])
@auth.login_required
def update_user(user_id):
    try:
        controller.update_user(g.user, request.json)
        return _show_success()
    except Exception as e:
        return _show_error(str(e))


@app.route(USER_ROUTE, methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    try:
        controller.delete_user(user_id)
        return _show_success()
    except Exception as e:
        return _show_error(str(e))


def _show_success():
    return {
        'result': 'success',
        'message': 'success'
    }


def _show_error(error_text, code=400):
    return {
        'result': 'error',
        'message': error_text
    }, code


def _fetch_procore_token(name: str = ''):
    return g.user.procore_data.get_token()


def _update_procore_token(token: dict, refresh_token: str = '', access_token: str = ''):
    user = g.user
    if not user:
        raise Exception('User not logged in')
    
    user.set_procore_token(token)
    controller.update_user(user)

