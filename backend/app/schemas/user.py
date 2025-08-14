from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    employee_code: Optional[str] = None
    phone_number: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    status: str
    role_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    status: str
    employee_code: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True