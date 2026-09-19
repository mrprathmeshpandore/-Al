import hashlib
import os

def hash_password(password: str) -> str:
    """
    Generates a secure password hash with a salt.
    """
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{pwd_hash.hex()}"

def verify_password(plain_password: str, stored_password_hash: str) -> bool:
    """
    Verifies a plain password against the stored salted hash.
    """
    try:
        salt_hex, hash_hex = stored_password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000).hex()
        return expected_hash == hash_hex
    except Exception:
        return False
