from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, request, g, redirect, make_response
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
import json
import re
from typing import List

from .api_endpoints import *
from .controller import Controller
import controller.server_connector as connector
from util.utils import parallel_for, build_url
import models.db_interface as db_int


API_VERSION = 'v2'

INDEX_ROUTE = ''
LOGIN_ROUTE = f'{INDEX_ROUTE}/login'
REGISTER_ROUTE = f'{INDEX_ROUTE}/register'
PROCORE_AUTH_ROUTE = f'{INDEX_ROUTE}/authorize'
WEBHOOK_HANDLER_ROUTE = f'{INDEX_ROUTE}/webhook_handler'
GCAL_LOGIN_ROUTE = f'{INDEX_ROUTE}/gcal_login'
GCAL_COLLABORATOR_LOGIN_ROUTE = f'{INDEX_ROUTE}/gcal_login_collab/<collaborator_id>'
GCAL_AUTH_ROUTE = f'{INDEX_ROUTE}/gcal_authorize'
USER_ROUTE = f'{INDEX_ROUTE}/users/<user_id>'


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
controller: Controller = None

oauth: OAuth = None

config_file = 'secrets/app.config'
with open(config_file, 'r') as f:
    config_contents = f.read()
config = json.loads(config_contents)


def create_app(cont: Controller) -> Flask:
    global app, auth, controller, oauth

    CORS(app, origins=[
        r'https?:\/\/[^\/]+\.procore\.com.*', 
        r'https?:\/\/localhost[^\.]*$',
        r'https?:\/\/ui[^\.]*$'])

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

@app.before_request
def start_db_session():
    # HACK: don't love the fact that I'm reaching into the DB interface
    db_int.session = db_int.createSession()
    g.session = db_int.session

@app.after_request
def close_db_session(resp):
    g.session.close()
    return resp

@auth.verify_token
def verify_token(token):
    token = extract_token(token)
    if not token:
        return None

    user = controller.get_user_from_token(token)
    if not user:
        return None

    g.user = user
    return user


def extract_token(token_str: str):
    idx = token_str.find('=')
    return token_str[idx+1:]


@app.route(LOGIN_ROUTE)
def login():
    redirect_uri = _create_redirect_uri(url_for('authorize', _external=True), PROCORE_AUTH_ROUTE)
    return oauth.procore.authorize_redirect(redirect_uri)


def _create_redirect_uri(base_uri, replace):
    redirect_uri = base_uri
    if config.get('ENV') != 'development':
        redirect_uri = redirect_uri.replace(replace, f'/api{replace}')
        redirect_uri = re.sub(r'https?://', 'https://', redirect_uri)
    return redirect_uri


@app.route(PROCORE_AUTH_ROUTE)
def authorize():
    token = oauth.procore.authorize_access_token()

    try: 
        user = controller.init_user(token)
        if user.procore_data.token.access_token != token.get('access_token'):
            user.set_procore_token(token)
            controller.update_user(user)

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

def _parse_webhook(data: dict) -> dict:
    out_dict = {}
    attrs = 'project_id resource_name resource_id'.split()
    for attr in attrs:
        value = data.get(attr)
        if not value:
            raise Exception(f'Missing {attr}')
        out_dict[attr] = value
    return out_dict


@app.route(GCAL_LOGIN_ROUTE)
def gcal_login():
    auth_token = extract_token(request.args.get('auth_token'))

    redirect_uri = _create_redirect_uri(url_for('gcal_authorize', _external=True), 
        GCAL_AUTH_ROUTE)
    return oauth.gcal.authorize_redirect(redirect_uri, state=auth_token, 
        access_type='offline', prompt='consent')


@app.route(GCAL_COLLABORATOR_LOGIN_ROUTE)
def gcal_collaborator_login(collaborator_id):
    redirect_uri = _create_redirect_uri(
        url_for('gcal_authorize', _external=True, collaborator=collaborator_id),
        GCAL_AUTH_ROUTE)
    return oauth.gcal.authorize_redirect(redirect_uri)


@app.route(GCAL_AUTH_ROUTE)
def gcal_authorize():
    gcal_token = oauth.gcal.authorize_access_token()
    auth_token = request.args.get('state')

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
    user.gcal_data.set_token(gcal_token)
    controller.update_user(user)
    return user


def _update_collaborator_gcal_token(token):
    collaborator_id = request.args.get('collaborator_id')
    if not collaborator_id:
        raise Exception('Malformed redirect URL')

    collaborator = controller.get_collaborator(collaborator_id)
    collaborator.gcal_data.set_token(token)
    controller.update_user(collaborator)
    return collaborator


def _redirect_to_collaborator_page(collaborator):
    path = f'/collaborators/{collaborator.id}'
    return _redirect_to_user_page(path, collaborator)


@app.route(USER_ROUTE, methods=['GET'])
@auth.login_required
def get_user(user_id):
    try:
        return controller.get_manager(g.user)
    except Exception as e:
        return _show_error(str(e))


@app.route(USER_ROUTE, methods=['PATCH'])
@auth.login_required
def update_user(user_id):
    try:
        g.user.temporary = False
        controller.update_user(g.user, request.json)
        return _show_success()
    except Exception as e:
        return _show_error(str(e))


@app.route(USER_ROUTE, methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    try:
        controller.delete_manager(user_id)
        return _show_success()
    except Exception as e:
        return _show_error(str(e))


def _show_success():
    return {
        'status': 'success',
        'message': 'success'
    }


def _show_error(error_text, code=400):
    return {
        'status': 'error',
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

