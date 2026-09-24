import secrets
import string

import bcrypt


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_password(char_quantity: int = 12) -> str:
    if char_quantity < 12:
        raise ValueError("Password quantity must be at least 12 characters")
    characters = string.ascii_letters + string.digits + string.punctuation
    return hash_password(
        "".join(secrets.choice(characters) for _ in range(char_quantity))
    )
