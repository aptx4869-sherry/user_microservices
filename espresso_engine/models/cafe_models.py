from pydantic import BaseModel, EmailStr, field_validator
import re
from zxcvbn import zxcvbn
from typing import Optional

# Model for Google token requests
class GoogleTokenRequest(BaseModel):
    token: str
    
# Model for user registration/login input
class User(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, v):
        """Strips whitespace from username and ensures it's not empty."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Username cannot be empty")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v, info):
        """Validates password strength based on various criteria."""
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
            
        # Access other fields for zxcvbn
        username = info.data.get("username", "")
        email = info.data.get("email", "")
        
        result = zxcvbn(v, user_inputs=[username, email])
        if result["score"] < 3: # Score 3 or higher is generally considered "good"
            feedback = "; ".join(result["feedback"]["suggestions"] or [result["feedback"]["warning"]])
            raise ValueError(f"Password too weak: {feedback}")

        return v

# Model for token responses
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str = "" 
    email: str = ""   