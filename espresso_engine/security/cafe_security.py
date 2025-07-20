from datetime import datetime, timedelta
from typing import Optional
import time
import secrets
import pytz
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from fastapi.responses import Response

# Import configurations from the config module
from config.cafe_config import ph, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_DAYS

# --- Password Hashing ---
def hash_password(password: str) -> str:
    """Hashes a plain-text password using Argon2."""
    return ph.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    try:
        return ph.verify(hashed, plain)
    except Exception: # Catch VerifyMismatchError and others
        return False

# --- JWT Token Management ---
def create_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    ist = pytz.timezone('Asia/Kolkata')
    
    expiry_utc = int(time.time()) + expires_delta
    expiry_ist = datetime.fromtimestamp(expiry_utc, tz=ist).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    to_encode.update({"exp_ist": expiry_ist,"exp": expiry_utc, "iat": int(time.time())})
    
    print(f"Creating access token payload: {to_encode}")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: int = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60) -> str:
    """Creates a JWT refresh token."""
    to_encode = data.copy()
    ist = pytz.timezone('Asia/Kolkata')
    
    expiry_utc = int(time.time()) + expires_delta
    expiry_ist = datetime.fromtimestamp(expiry_utc, tz=ist).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    to_encode.update({"exp_ist": expiry_ist,"exp": expiry_utc,"iat": int(time.time())})
    
    print(f"Creating refresh token payload: {to_encode}") 
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: Optional[str]) -> Optional[dict]:
    """Decodes and verifies a JWT token, returning the payload if valid."""
    if not token:
        print("Missing token")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except ExpiredSignatureError as e:
        print(f"Token has expired: {e}")
        return None
    except JWTError as e:
        print(f"Invalid token: {e}")
        return None

# --- CSRF Token Generation ---
def generate_csrf_token() -> str:
    """Generates a random CSRF token."""
    return secrets.token_hex(16)

# --- Cookie Management ---
def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str):
    """Sets authentication cookies (session, refresh, CSRF) on the response."""
    # session_token (access token) - short-lived, HttpOnly
    response.set_cookie(
        key="session_token", value=access_token, httponly=True,
        secure=False, # Set to True in production with HTTPS
        samesite="Lax", # "Lax" for most cases, "Strict" for stronger security
        max_age=ACCESS_TOKEN_EXPIRE_SECONDS # Matches token expiry
    )
    # refresh_token - longer-lived, HttpOnly
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True,
        secure=False, # Set to True in production with HTTPS
        samesite="Lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 # Matches token expiry
    )
    # csrf_token - for CSRF protection, NOT HttpOnly (needed by frontend JS)
    response.set_cookie(
        key="csrf_token", value=csrf_token, httponly=False,
        secure=False, # Set to True in production with HTTPS
        samesite="Lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 # Matches refresh token expiry
    )

def clear_auth_cookies(response: Response):
    """Clears authentication cookies."""
    response.delete_cookie(key="session_token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="csrf_token")