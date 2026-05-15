from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGORITHM = 'HS256'


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, secret_key: str, expires_minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {'sub': subject, 'exp': expire}
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> str | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload.get('sub')
    except JWTError:
        return None
