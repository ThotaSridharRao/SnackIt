from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.models import RoleEnum

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.customer
    preferred_language: str = "English"

class UserOut(UserBase):
    id: str
    role: RoleEnum
    preferred_language: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
