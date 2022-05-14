from __future__ import annotations

from app import db
from flask import current_app
from flask_httpauth import HTTPTokenAuth
from app.core.services import login
from datetime import datetime, timedelta
import jwt

# User authentication
authenticator: HTTPTokenAuth = HTTPTokenAuth(scheme="Bearer")
# Device Authentication
deviceAuthenticator: HTTPTokenAuth = HTTPTokenAuth(scheme="Bearer")

'''''''''''''''''''''''''''
    
    User Authentication

'''''''''''''''''''''''''''

def verify_user_credentials(username: str, password: str) -> bool:
    """
    Returns whether or not a user is logged in
    """
    return login(username, password, db.session)

@authenticator.verify_token
def verify_token(token: bytes):
    """
    Authentication function
    """
    if not current_app.config['AUTH_ENABLED']:
        return True

    return check_jwt_valid(token)

def belongs_to_user(request, user_id: int):

    token = request.headers['Authorization'].split(' ')[1]

    decoded = decode_jwt(token)

    return decoded['userId'] == user_id

def create_jwt(username, userId):

    encoded_jwt = jwt.encode({"user": username, "userId": userId, "expiryTime": str(datetime.now() + timedelta(days=3))}, current_app.config['SECRET_KEY'], algorithm="HS256")

    print(encoded_jwt)

    return encoded_jwt


def decode_jwt(enc_jwt):
    return jwt.decode(enc_jwt, current_app.config['SECRET_KEY'], algorithms=["HS256"])

def check_jwt_valid(enc_jwt):

    decoded_jwt = jwt.decode(enc_jwt, current_app.config['SECRET_KEY'], algorithms=["HS256"])

    if decoded_jwt['expiryTime'] == None or decoded_jwt['user'] == None:
        return False

    format = "%Y-%m-%d %H:%M:%S.%f"

    if datetime.strptime(decoded_jwt['expiryTime'], format) < datetime.now():
        return False

    return True


'''''''''''''''''''''''''''
    
    Device Authentication

'''''''''''''''''''''''''''

@deviceAuthenticator.verify_token
def check_device_token_valid(token):

    if not current_app.config['AUTH_ENABLED']:
        return True

    try:
        decoded_jwt = jwt.decode(token, current_app.config['SECRET-KEY'], algorithms=['HS256'])
        if decoded_jwt['deviceId'] is None or decoded_jwt['deviceId'] == None:
            return False
    except:
        return False
    return True

def create_device_jwt(deviceId, userId):
    encoded_jwt = jwt.encode({ "deviceId": deviceId, "userId": userId }, current_app.config['SECRET-KEY'], algorithm="HS256")
    return encoded_jwt

def decode_device_jwt(enc_jwt):
    return jwt.decode(enc_jwt, current_app.config['SECRET-KEY'], algorithms=['HS256'])
