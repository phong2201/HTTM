from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from .base_schema import ICTBaseModel

class UserBase(BaseModel):
    username: str
    email: str
    role_id: Optional[int] = None
    gender: Optional[str] = None
    age: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(ICTBaseModel, UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class RoleUpdate(BaseModel):
    role_id: int
    
class UserRoleResponse(BaseModel):
    username: str
    new_role: int