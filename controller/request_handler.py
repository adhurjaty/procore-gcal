from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for
from flask_cors import CORS
import json
import requests


class TempCache:
    def get(self, key):
        pass

    def set(self, key, value, expires=None):
        pass


app = Flask(__name__)

config_file = 'secrets/app.config'
with open(config_file, 'r') as f:
    config_contents = f.read()
config = json.loads(config_contents)
app.config.update(**config)

app.secret_key = app.config['APP_SECRET']

cache = TempCache()
oauth = OAuth(app, cache=cache)
oauth.register('procore')


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
    resp = oauth.procore.get('account/verify_credentials.json')
    profile = resp.json()
    return ''


app.run(host='0.0.0.0')