import jwt
import datetime
from flask import current_app

# The Secret Key (Keep this in your .env file, NEVER in code)
# SECRET_KEY = "s0me-r4nd0m-str1ng"

def encode_auth_token(user_id):
    """
    Generates the Auth Token (The ID Badge)
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1), # Expires in 1 day
            'iat': datetime.datetime.utcnow(), # Issued At
            'sub': user_id, # The Subject (User ID)
            'scope': 'tier_1' # You can bake permissions right into the token!
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e