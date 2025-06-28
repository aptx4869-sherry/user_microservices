from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from pydantic import BaseModel

router = APIRouter()

# Dummy in-memory store passed from main app
users = []

# Response model (no password exposed)
class UserOut(BaseModel):
    username: str
    email: str

@router.get("/brewboard", response_model=List[UserOut])
def get_all_users():
    if not users:
        raise HTTPException(status_code=404, detail="No brewers found ☕️")
    return users
