from fastapi import APIRouter, Response, Request, Cookie, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import secrets
from ..routes.cafe_auth_routes import create_token, verify_token, clear_auth_cookies

import uuid

router = APIRouter(prefix="/auth", tags=["auth"])
ACCESS_TOKEN_EXPIRE_SECONDS =  1800

def verify_csrf_token(header_token: Optional[str], cookie_token: Optional[str]) -> bool:

    if not header_token or not cookie_token:
        return False
    return secrets.compare_digest(header_token, cookie_token)

@router.post("/refresh")
def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),
    csrf_token: str = Cookie(None),
    csrf_header: str = Header(None, alias="X-CSRF-TOKEN")
):  

    if not verify_csrf_token(csrf_header, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user_id = str(uuid.uuid4())
  
    new_token = create_token({"sub": user_id, "type" : "access"})
    response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age= ACCESS_TOKEN_EXPIRE_SECONDS
    )
    
    return {"access_token": new_token}

# Logout endpoint
@router.post("/logout")
async def logout_user_endpoint(response: Response, csrf_token: Optional[str] = Header(None), csrf_cookie: Optional[str] = Cookie(None)):
    """Logs out the user by clearing authentication cookies."""
    # CSRF protection for logout
    if csrf_token != csrf_cookie:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
        
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}
