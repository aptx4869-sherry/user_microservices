from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
import hashlib, hmac, base64, secrets, time, json, re

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# In-memory user store and secret key
users = []
SECRET_KEY = secrets.token_bytes(32)

# User input model
class User(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, v):
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Username cannot be empty")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must include at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must include at least one special character")
        return v

# Token response model
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Hash the password with a generated salt
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

# Verify entered password against stored hash
def verify_password(plain: str, hashed: str) -> bool:
    salt, hashed_val = hashed.split('$')
    return hashed_val == hashlib.sha256((salt + plain).encode()).hexdigest()

# Generate a simple HMAC-based access token
def create_token(data: dict, expires_in: int = 1800) -> str:
    payload = {
        "data": data,
        "exp": int(time.time()) + expires_in
    }
    payload_bytes = json.dumps(payload).encode()
    signature = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(payload_bytes + b"." + signature).decode()
    return token

# Decode and verify token, return payload if valid
def verify_token(token: str) -> Optional[dict]:
    try:
        token_bytes = base64.urlsafe_b64decode(token.encode())
        payload_bytes, signature = token_bytes.rsplit(b".", 1)
        expected_signature = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = json.loads(payload_bytes.decode())
        if payload["exp"] < int(time.time()):
            return None

        return payload["data"]
    except Exception:
        return None

# Register endpoint: hash password, store user, return token
@router.post("/register", response_model=Token)
@limiter.limit("1/minute")
def register_user(user: User, request: Request):
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    users.append({"username": user.username, "email": user.email, "password": hashed_pwd})

    token = create_token({"email": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Session check endpoint
@router.get("/session")
def check_session(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Session expired or token invalid")

    return {"message": "Session is valid", "user": user_data}

