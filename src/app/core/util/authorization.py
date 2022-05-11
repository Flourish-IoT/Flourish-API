from bcrypt import checkpw, gensalt, hashpw

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