from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, request
from flask_cors import CORS
import json
import requests
from .controller import Controller
from .api_endpoints import PROCORE_GET_USER

app = Flask(__name__)

config_file = 'secrets/app.config'
with open(config_file, 'r') as f:
    config_contents = f.read()
config = json.loads(config_contents)
app.config.update(**config)

app.secret_key = app.config['APP_SECRET']

controller = Controller()

oauth = OAuth(app)
oauth.register('procore', fetch_token=controller.get_token, 
    update_token=controller.update_token)

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


def get_procore_user_from_token(token):
    result = oauth.procore.get(PROCORE_GET_USER)
    return result.json()


@app.route('/test')
def test():
    resp = oauth.procore.get('/vapid/projects?company_id=26972')
    return resp.json()[0]


@app.route('/event_webhook', methods=['POST'])
def event_webhook():
    pass


def show_success():
    return {
        'result': 'success'
    }


def show_error(error_text):
    return {
        'result': 'error',
        'error': error_text
    }
