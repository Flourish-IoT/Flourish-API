from __future__ import annotations

from bcrypt import checkpw, gensalt, hashpw
from jwt import decode, encode

KEY: str = ""

def decrypt_jwt(token: bytes) -> dict:
    """
    Decrypts a JWT into a python dictionary object
    """
    return decode(token)
    
def encrypt_jwt(data: dict) -> bytes:
    """
    Encrypts a python dictionary object into a JWT byte array
    """
    return encode(data, KEY)

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
