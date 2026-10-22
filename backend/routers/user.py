from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user_model import User
from database import get_db
from dependencies.auth_deps import require_admin, get_current_user
from schemas.user_schema import UserResponse
from schemas.base_schema import IMessageResponse
from uuid import UUID
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.created_at.desc()).limit(100).all()


@router.delete("/{user_id}", response_model=IMessageResponse)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính tài khoản đang đăng nhập")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    db.delete(user)
    db.commit()
    return {"message": "Đã xóa người dùng"}
