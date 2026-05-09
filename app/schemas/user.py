from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserDTO(BaseModel):
    id: int
    name: str
    email: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponseDTO(BaseModel):
    token: str
    user: UserDTO


def user_schema(user_obj):
    if not user_obj:
        return None

    return {
        "id": user_obj.id,
        "name": user_obj.name,
        "email": user_obj.email,
        "created_at": user_obj.created_at.isoformat() if user_obj.created_at else None,
    }


def users_list_schema(users_list):
    return [user_schema(user) for user in users_list]
