from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import jwt
from pwdlib.hashers.bcrypt import BcryptHasher
from app.core.config import settings

hasher = BcryptHasher()


def hash_password(password: str) -> str:
    """
    Generates a secure password hash using bcrypt.
    """
    return hasher.hash(password)


def verify_password(plain_password: str, stored_password_hash: str) -> bool:
    """
    Verifies a plain password against the stored bcrypt hash (with backward compatibility if needed).
    """
    if not stored_password_hash:
        return False
    try:
        return hasher.verify(plain_password, stored_password_hash)
    except Exception:
        # Fallback for PBKDF2 if old hashes exist
        try:
            import hashlib
            salt_hex, hash_hex = stored_password_hash.split(':')
            salt = bytes.fromhex(salt_hex)
            expected_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000).hex()
            return expected_hash == hash_hex
        except Exception:
            return False


def create_access_token(subject: Any, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token containing only non-sensitive claims (sub, email, exp, iat).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "email": email,
        "exp": expire,
        "iat": now,
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a JWT access token.
    Returns payload dictionary or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
