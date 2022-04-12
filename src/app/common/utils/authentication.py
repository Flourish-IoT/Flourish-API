from __future__ import annotations

from app import db
from bcrypt import checkpw, gensalt, hashpw
# from jwt import decode, encode
from flask_httpauth import HTTPTokenAuth
from app.core.services import login

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
    decrypted_credentials: dict = decrypt_jwt(token)
    username: str = decrypted_credentials.get("username")
    password: str = decrypted_credentials.get("password")
    return decrypted_credentials if verify_user_credentials(username, password) else None

# def decrypt_jwt(token: bytes) -> dict:
#     """
#     Decrypts a JWT into a python dictionary object
#     """
#     return decode(token, KEY)
    
# def encrypt_jwt(data: dict) -> bytes:
#     """
#     Encrypts a python dictionary object into a JWT byte array
#     """
#     return encode(data, KEY)

def hash_password(unhashed_password: str) -> str:
    """
    Transforms a plain-text password string into a hashed one
    """
    return hashpw(unhashed_password, gensalt())

def check_password(password: str, hashed_password: str) -> bool:
    """
    Checks if an unhashed password matches its hashed counterpart
    """
    return checkpw(password, hashed_password)
