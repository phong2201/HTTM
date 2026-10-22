from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas.auth_schema import TokenResponse
from schemas.user_schema import UserResponse, UserCreate, RoleUpdate, UserRoleResponse
from uuid import UUID
from core.security import verify_password, create_access_token
import repositories.user_repository as user_repo


async def register_user(user_in: UserCreate, db: Session) -> UserResponse:
    """Đăng ký tài khoản mới"""
    if user_repo.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    if user_repo.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Tài khoản email này đã được đăng ký")

    return user_repo.create_user(db, user_in)


async def login(form_data: OAuth2PasswordRequestForm, db: Session) -> TokenResponse:
    """Đăng nhập và trả về access token"""
    user = user_repo.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


async def update_user_role(username: str, role_in: RoleUpdate, db: Session) -> UserRoleResponse:
    """Service xử lý logic cập nhật vai trò người dùng"""
    updated_user = user_repo.update_user_role(db, username, role_in.role_id)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng")
    
    return UserRoleResponse(
        username=updated_user.username,
        new_role=updated_user.role_id
    )
