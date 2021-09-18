import time
from typing import Dict

import jwt


def token_response(token: str):
    return {
        "access_token": token
    }


JWT_SECRET = 'this_is_my_jwt_secret'


def sign_jwt(email: str) -> Dict[str, str]:
    # Set the expiry time.
    payload = {
        'email': email,
        'expires': time.time() + 3600
    }
    return token_response(jwt.encode(payload, JWT_SECRET, algorithm="HS256"))


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token.encode(), JWT_SECRET, algorithms=["HS256"])
        return decoded_token if decoded_token['expires'] >= time.time() else None
    except:
        return None
