from base64 import b64encode, b64decode
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
from multiprocessing import Process
import os
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse, urlencode, urlunparse


script_dir = os.path.dirname(os.path.abspath(__file__))
secrets_dir = os.path.join(script_dir, '..', 'secrets')
PRIVATE_KEY_FILE = os.path.join(secrets_dir, 'csrf_token_key.pem')
config_file = os.path.join(secrets_dir, 'app.config')


def parallel_for(fn, arg_list):
    lock = Lock()
    out_list = []

    def return_proc(arg):
        value = fn(arg)
        with lock:
            out_list.append(value)

    def start_proc(arg):
        p = Process(target=return_proc(arg))
        p.start()
        return p

    procs = [start_proc(arg) for arg in arg_list]
    for p in procs:
        p.join()

    return out_list


def build_url(base_url: str, path: str, args_dict: dict) -> str:
    url_parts = list(urlparse(base_url))
    url_parts[2] = path
    url_parts[4] = urlencode(args_dict)
    return urlunparse(url_parts)


def get_signed_token(oauth_token: str) -> str:
    digest = SHA256.new()
    digest.update(oauth_token.encode('utf-8'))

    private_key = get_private_key()
    
    signer = PKCS1_v1_5.new(private_key)
    return b64encode(signer.sign(digest)).decode('utf-8')


def get_private_key():
    with open(PRIVATE_KEY_FILE, 'r') as f:
        return RSA.importKey(f.read())


def verify_token(oauth_token: str, sig: str) -> bool:
    digest = SHA256.new()
    digest.update(oauth_token.encode('utf-8'))

    private_key = get_private_key()

    verifier = PKCS1_v1_5.new(private_key.publickey())
    return verifier.verify(digest, b64decode(sig))


def get_config() -> dict:
    with open(config_file, 'r') as f:
        return json.load(f)


def get_trial_period_days() -> int:
    return get_config().get('TRIAL_PERIOD')

