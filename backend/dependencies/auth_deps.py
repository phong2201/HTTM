from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from models.user_model import User, Role
from core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không chứa user_id"
        )
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token chứa user_id không hợp lệ"
        )
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tài khoản không tồn tại hoặc đã bị khóa")
    return user 


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != Role.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập. Yêu cầu quyền Admin.")
    return current_user

async def require_data_scientist(current_user: User = Depends(get_current_user)) -> User:
    """Data Scientist; Admin cũng được vào."""
    if current_user.role_id not in (Role.DATA_SCIENTIST.value, Role.ADMIN.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập. Yêu cầu quyền Data Scientist.")
    return current_user

async def require_seller(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != Role.SELLER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không đủ quyền truy cập. Yêu cầu quyền Seller.")
    return current_user
