from fastapi import APIRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from argon2 import PasswordHasher
import secrets
import os
from dotenv import load_dotenv

# Load environment variables (ensure .env is in your project root)
load_dotenv()

# --- Global Configurations ---
# Google Client ID from environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable not set. Please set it in your .env file.")

# JWT Configuration
# For development, secrets.token_urlsafe(32) provides a random key each time the server starts.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 1800 # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Argon2 Password Hasher Configuration
ph = PasswordHasher(
    time_cost=3,       # number of iterations
    memory_cost=65536, # in KB (64 MB)
    parallelism=2,     # threads
    hash_len=32,
    salt_len=16
)

# FastAPI Router instance
# This router will be imported by other route files to define their endpoints.
router = APIRouter()

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address)