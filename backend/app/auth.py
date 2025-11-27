from datetime import datetime, timedelta
from typing import Optional
import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "your-secret-key":
    raise RuntimeError("SECRET_KEY environment variable must be set for JWT signing.")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_ISSUER = os.getenv("JWT_ISSUER", "article-generator.api")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    issued_at = datetime.utcnow()
    if expires_delta:
        expire = issued_at + expires_delta
    else:
        expire = issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {
            "exp": expire,
            "iat": issued_at,
            "nbf": issued_at,
            "iss": JWT_ISSUER,
        }
    )
    if JWT_AUDIENCE:
        to_encode["aud"] = JWT_AUDIENCE
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decode_kwargs = {
            "key": SECRET_KEY,
            "algorithms": [ALGORITHM],
            "issuer": JWT_ISSUER,
        }
        if JWT_AUDIENCE:
            decode_kwargs["audience"] = JWT_AUDIENCE
        else:
            # jose requires verify_aud False when audience missing
            decode_kwargs["options"] = {"verify_aud": False}
        payload = jwt.decode(token, **decode_kwargs)
        return payload
    except JWTError:
        return None
