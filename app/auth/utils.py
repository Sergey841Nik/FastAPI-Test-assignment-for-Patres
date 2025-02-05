from datetime import datetime, timezone, timedelta

import bcrypt
import jwt

from ..config import settings


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt() 
    pwd_byts: bytes = password.encode() 
    return bcrypt.hashpw(pwd_byts, salt)  #создаём хэш пароля

def validate_password(password: str, hash_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash_password.encode()) #проверяем хэш пароля

#создаём jwt
def encoded_jwt(
        payload: dict, 
        private_key: str = settings.private_key_path.read_text(),
        algorithm: str = settings.algorithms,
        expire_timedelta: timedelta | None = None,
        expire_min: int = settings.access_token_expire_min, 
):
    to_encoded = payload.copy() 
    now = datetime.now(tz=timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_min)
    to_encoded.update(exp=expire, iat=now,) 
    encoded = jwt.encode(to_encoded, private_key, algorithm=algorithm)
    return encoded

#создаём расшифровщик
def decoded_jwt(
        token: str | bytes,
        public_key: str = settings.public_key_path.read_text(),
        algorithm: str = settings.algorithms,
) -> dict[str, str]:
    
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded