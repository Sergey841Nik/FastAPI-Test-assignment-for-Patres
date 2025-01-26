from datetime import datetime, timezone, timedelta
from logging import getLogger

import bcrypt
import jwt

from ..config import settings

logger = getLogger(__name__)

def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt() 
    pwd_byts: bytes = password.encode() 
    return bcrypt.hashpw(pwd_byts, salt)  #создаём хэш пароля

def validate_password(password: str, hash_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash_password) #проверяем хэш пароля

#создаём jwt
def encoded_jwt(
        payload: dict, 
        private_key: str = settings.private_key_path.read_text(),
        algorithm: str = settings.algorithms,
        expire_timedelta: timedelta | None = None,
        expire_days: int = settings.access_token_expire_day, 
):
    to_encoded = payload.copy() 
    now = datetime.now(tz=timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(days=expire_days)
    to_encoded.update(exp=expire, iat=now,) 
    encoded = jwt.encode(to_encoded, private_key, algorithm=algorithm)
    return encoded

#создаём расшифровщик
def decoded_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithms,
) -> dict[str, str]:
    logger.info("token: %s" % token)
    
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded