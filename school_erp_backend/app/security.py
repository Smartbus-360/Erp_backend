from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os

# ------------------------------------------------------------------
# Password hashing context (bcrypt)
# ------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ------------------------------------------------------------------
# JWT configuration
# ------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

# ------------------------------------------------------------------
# Password helpers
# NOTE: bcrypt supports max 72 bytes → we enforce it
# ------------------------------------------------------------------
def hash_password(password: str) -> str:
    password = password.encode("utf-8")[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------------------------------------------------
# JWT token creator
# ------------------------------------------------------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
