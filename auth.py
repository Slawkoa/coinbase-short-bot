import jwt
import time
import yaml

def load_config(path='config.yaml'):
    with open(path) as f:
        for doc in yaml.safe_load_all(f):
            if isinstance(doc, dict):
                return doc
    return {}

cfg = load_config()
key_name = cfg.get('key_name')
private_key = cfg.get('private_key')

def get_jwt():
    now = int(time.time())
    payload = {'iat': now, 'exp': now + 300, 'iss': key_name}
    token = jwt.encode(payload, private_key, algorithm='ES256')
    return token
