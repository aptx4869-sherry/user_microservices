from fastapi import HTTPException, Header, Request, Response, Cookie
from typing import Optional
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Import shared router, limiter, and GOOGLE_CLIENT_ID from config
from config.cafe_config import router, limiter, GOOGLE_CLIENT_ID

# Import models
from models.cafe_models import User, GoogleTokenRequest, Token

# Import data storage functions
from data.cafe_data_storage import users, get_user_by_email, add_user

# Import security functions
from security.cafe_security import (
    hash_password, verify_password, create_token,
    create_refresh_token, verify_token, generate_csrf_token,
    set_auth_cookies, clear_auth_cookies
)

import uuid

# Register endpoint: hash password, store user, return token
@router.post("/register", response_model=Token)
@limiter.limit("3/minute") # Apply rate limiting
async def register_user(user: User, request: Request, response: Response):
    """Registers a new user with email and password."""
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    user_id = str(uuid.uuid4())
    add_user({"username": user.username, "email": user.email, "password": hashed_pwd, "sub" : user_id})

    access_token = create_token({"sub": user_id })
    refresh_token = create_refresh_token({"sub": user_id})
    
    csrf_token = generate_csrf_token()
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    
    return {"access_token": access_token, "token_type": "bearer"}

# Login endpoint
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_user(user_credentials: User, request: Request, response: Response):
    """Authenticates a user with email and password."""
    user = get_user_by_email(user_credentials.email)
    user_id = str(uuid.uuid4())
    
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    csrf_token = generate_csrf_token()
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    
    return {"access_token": access_token, "token_type": "bearer", "username": user["username"], "email": user["email"]}


# Session check endpoint (using Authorization header)
@router.get("/session")
async def check_session_header(authorization: Optional[str] = Header(None)):
    """Checks the validity of the session token provided in the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    user_data = verify_token(token)
    if not user_data or user_data.get("type") != "access": # Ensure it's an access token
        raise HTTPException(status_code=401, detail="Session expired or token invalid")

    return {"message": "Session is valid", "username": user_data.get("username"), "email": user_data.get("email")}

# Endpoint to provide Google Client ID to frontend
@router.get("/config/google-client-id")
async def get_google_client_id():
    """Returns the Google Client ID for frontend integration."""
    return {"client_id": GOOGLE_CLIENT_ID}

# Google registration/login endpoint
@router.post("/google-register", response_model=Token)
async def google_register(data: GoogleTokenRequest, response: Response):
    """Handles Google Sign-In/Registration."""
    try:
        # Verify the Google ID token with Google's servers
        id_info = id_token.verify_oauth2_token(
            data.token, google_requests.Request(), audience=GOOGLE_CLIENT_ID, clock_skew_in_seconds=5 
        )
        
        email = id_info.get("email")
        name = id_info.get("name") or email.split("@")[0] # Fallback for username
        user_id = str(uuid.uuid4())
        # Check if user already exists in our system
        user_exists = get_user_by_email(email)

        # Create new tokens
        access_token = create_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})
        csrf_token = generate_csrf_token()

        if not user_exists:
            # If user doesn't exist, add them to our in-memory store
            add_user({"username": name, "email": email, "password": None}) # Password is None for Google users
            print(f"New Google user registered: {email}")
        else:
            print(f"Existing Google user logged in: {email}")
        
        # Set authentication cookies
        set_auth_cookies(response, access_token, refresh_token, csrf_token)
        
        return {"access_token": access_token, "token_type": "bearer", "username": name, "email": email}

    except ValueError as e:
        print(f"Google token verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        print(f"An unexpected error occurred during Google registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during Google login")


# Cookie validation endpoint (for session refresh/check via cookies)
@router.get("/cookie-validate")
async def check_session_cookies(request: Request, response: Response):
    """Validates session and refresh tokens from cookies."""
    session_token = request.cookies.get("session_token")
    refresh_token = request.cookies.get("refresh_token")
    csrf_token_header = request.headers.get("X-CSRF-Token")
    csrf_token_cookie = request.cookies.get("csrf_token")

    print(f"Received session_token: {session_token}")
    print(f"Received refresh_token: {refresh_token}")
    # print(f"Received X-CSRF-Token header: {csrf_token_header}")
    print(f"Received csrf_token cookie: {csrf_token_cookie}")

    # CSRF check (important for state-changing requests, but good to include for session check too)
    # if csrf_token_header != csrf_token_cookie:
        # print("CSRF token mismatch!")
        # For a GET request, you might just log, but for POST/PUT/DELETE, this should be a 403
        # raise HTTPException(status_code=403, detail="CSRF token mismatch")

    # Try access token first
    if session_token:
        payload = verify_token(session_token)
        if payload and payload.get("type") == "access":
            print("Access token is valid.")
            return {"username": payload.get("username"), "email": payload.get("email"), "message": "Session valid via access token", "type": "access"}

    # If access token is missing or invalid, try refresh token
    if refresh_token:
        print("Access token invalid or missing, attempting refresh token.")
        payload = verify_token(refresh_token)
        user_id = str(uuid.uuid4())
        
        if payload and payload.get("type") == "refresh":
            print("Refresh token is valid. Issuing new access token.")
            # Issue new access token and refresh token (optional: rotate refresh token)
            new_access_token = create_token({"sub": user_id})
            new_refresh_token = create_refresh_token({"sub": user_id}) # Optional: rotate refresh token
            new_csrf_token = generate_csrf_token() # Generate new CSRF token
            
            set_auth_cookies(response, new_access_token, new_refresh_token, new_csrf_token)
            
            return {"sub": user_id, "message": "Session refreshed", "type": "refresh"}
        else:
            print("Refresh token is invalid or expired.")

    # If neither token is valid, clear cookies and raise unauthorized
    print("Neither session nor refresh token is valid. Clearing cookies.")
    clear_auth_cookies(response)
    raise HTTPException(status_code=401, detail="Not logged in or session expired")
