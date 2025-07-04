import jwt
import time
import yaml

def load_config(path='config.yaml'):
    with open(path) as f:
        return yaml.safe_load(f)

cfg = load_config()
key_name = cfg['key_name']
private_key = cfg['private_key']

def get_jwt():
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + 300,
        'iss': key_name,
    }
    token = jwt.encode(payload, private_key, algorithm='ES256')
    return token
