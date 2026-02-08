from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import hashlib
from fastapi import Depends, HTTPException, status

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def normalize_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
def hash_password(password: str):
    normalized = normalize_password(password)
    return pwd_context.hash(normalized)
def verify_password(plain_password, hashed_password):
    normalized = normalize_password(plain_password)
    return pwd_context.verify(normalized, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Create JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from fastapi import Depends, HTTPException, status
from jose import JWTError

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user