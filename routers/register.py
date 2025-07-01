from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
import secrets, time, re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from zxcvbn import zxcvbn
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.get("/", include_in_schema=False)
def serve_frontend():
    file_path = Path(__file__).parent.parent / "frontend" / "index.html"
    return FileResponse(file_path)


limiter = Limiter(key_func=get_remote_address)
ph = PasswordHasher(
    time_cost=3,       # number of iterations
    memory_cost=65536, # in KB (64 MB)
    parallelism=2,     # threads
    hash_len=32,
    salt_len=16
)


# In-memory user store and secret key
users = []

# JWT config
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 1800

class GoogleTokenRequest(BaseModel):
    token: str
    
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
    def validate_password_strength(cls, v, values):
        v = v.strip()
        if " " in v:
            raise ValueError("Password must not contain spaces")
        if len(v) > 64:
            raise ValueError("Password must not exceed 64 characters")
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
            
        username = values.data.get("username", "") if values else ""
        email = values.data.get("email", "") if values else ""
        
        result = zxcvbn(v, user_inputs=[username, email])
        if result["score"] < 3:
            feedback = "; ".join(result["feedback"]["suggestions"] or [result["feedback"]["warning"]])
            raise ValueError(f"Password too weak: {feedback}")

        return v

# Token response model
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Verify entered password against stored hash
def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False

def create_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS):
    to_encode = {"sub": data["email"], "exp": int(time.time()) + expires_delta}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode and verify token, return payload if valid
def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except JWTError:
        return None

# Register endpoint: hash password, store user, return token
@router.post("/register", response_model=Token)
@limiter.limit("3/minute")
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

@router.get("/config/google-client-id")
def get_google_client_id():
    return {"client_id": os.getenv("GOOGLE_CLIENT_ID")}

@router.post("/google-register", response_model=Token)
def google_register(data: GoogleTokenRequest):
    try:
        id_info = id_token.verify_oauth2_token(
            data.token, google_requests.Request(), audience=GOOGLE_CLIENT_ID
        )

        
        email = id_info.get("email")
        name = id_info.get("name") or email.split("@")[0]

        if any(u["email"] == email for u in users):
            token = create_token({"email": email})
            return {"access_token": token, "token_type": "bearer"}

        users.append({"username": name, "email": email, "password": None})
        token = create_token({"email": email})
        return {"access_token": token, "token_type": "bearer"}

    except ValueError as e:
        print("Token verification failed:", e)
        raise HTTPException(status_code=400, detail="Invalid Google token")
