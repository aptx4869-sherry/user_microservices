from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict

# Import the shared router instance
from config.cafe_config import router
from data.cafe_data_storage import users 

class UserOut(BaseModel):
    username: str
    email: str

@router.get("/brewboard", response_model=List[UserOut])
def get_all_users():
    if not users:
        raise HTTPException(status_code=404, detail="No brewers found ☕️")
    return users