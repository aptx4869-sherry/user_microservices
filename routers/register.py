
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List

app = FastAPI()

# In-memory storage (for now)
users = []

class User(BaseModel):
    username: str
    email: EmailStr
    password: str

@app.post("/register")
def register_user(user: User):
    # Check for existing user
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    users.append(user.dict())
    return {"message": "User registered successfully", "user": user.username}
