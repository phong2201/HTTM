from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models.user_model import User
from database import get_db
from dependencies.auth_deps import require_admin, get_current_user
from schemas.auth_schema import TokenResponse
from schemas.user_schema import UserResponse, UserCreate, RoleUpdate, UserRoleResponse
from uuid import UUID

import services.auth_service as auth_service
router = APIRouter()

# Đăng ký
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return await auth_service.register_user(user_in, db)


# Đăng nhập
@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return await auth_service.login(form_data, db)


# Chỉnh sửa vai trò người dùng - chỉ ADMIN 
@router.patch("/{username}/role", response_model=UserRoleResponse)
async def update_user_role(
    username: str, 
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await auth_service.update_user_role(username, role_in, db)

