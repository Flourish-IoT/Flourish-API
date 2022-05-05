from __future__ import annotations

from app import db
from bcrypt import checkpw, gensalt, hashpw
# from jwt import decode, encode
from flask_httpauth import HTTPTokenAuth
from app.core.services import login
from datetime import datetime, timedelta
from base64 import decode, encode
from json import dumps, load
import jwt

KEY: str = "SECRET-KEY"  # TODO: Move to configuration

authenticator: HTTPTokenAuth = HTTPTokenAuth(scheme="Bearer")

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
    return check_jwt_valid(token)

# def decrypt_jwt(token: bytes) -> dict:
#     """
#     Decrypts a JWT into a python dictionary object
#     """
#     return decode(token, KEY)

def belongs_to_user(request, user_id: int):

    token = request.headers['Authorization'].split(' ')[1]
    
    decoded = decode_jwt(token)

    return decoded['userId'] == user_id

def create_jwt(username, userId):
    
    encoded_jwt = jwt.encode({"user": username, "userId": userId, "expiryTime": str(datetime.now() + timedelta(days=3))}, KEY, algorithm="HS256")

    print(encoded_jwt)

    return encoded_jwt


def decode_jwt(enc_jwt):
    return jwt.decode(enc_jwt, KEY, algorithms=["HS256"])

def check_jwt_valid(enc_jwt):

    decoded_jwt = jwt.decode(enc_jwt, KEY, algorithms=["HS256"])

    #print(decoded_jwt)

    if decoded_jwt['expiryTime'] == None or decoded_jwt['user'] == None:
        return False

    format = "%Y-%m-%d %H:%M:%S.%f"

    if datetime.strptime(decoded_jwt['expiryTime'], format) < datetime.now():
        return False

    return True

# def encrypt_jwt(data: dict) -> bytes:
#     """
#     Encrypts a python dictionary object into a JWT byte array
#     """
#     return encode(data, KEY)

def hash_password(unhashed_password: str) -> str:
    """
    Transforms a plain-text password string into a hashed one
    """
    return hashpw(unhashed_password, gensalt()).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
    Checks if an unhashed password matches its hashed counterpart
    """
    return checkpw(password, hashed_password)
