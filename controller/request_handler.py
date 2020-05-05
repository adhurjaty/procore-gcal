from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, request
from flask_cors import CORS
import json
import requests
from .controller import Controller

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


@app.route('/authorize')
def authorize():
    token = oauth.procore.authorize_access_token()
    controller.save_token(**token)
    return 'login success'


@app.route('/test')
def test():
    resp = oauth.procore.get('/vapid/projects')
    return 'success'