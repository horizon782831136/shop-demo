from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    # Fix #7: 强制密码最小长度为 8 位，防止弱密码注册
    password: str = Field(min_length=8)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_admin: bool
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str
