import jwt
import time
from config import config

private_key = config("qweather_api_key")

payload = {
    'iat': int(time.time()) - 30,
    'exp': int(time.time()) + 30,
    'sub': config("qweather_project_id"),
}
headers = {
    'kid': config("qweather_key_id"),
}

# Generate JWT
def generate_jwt():
    """
    Generate JWT token
    :return: JWT token
    """
    return jwt.encode(payload, private_key, algorithm='EdDSA', headers = headers)