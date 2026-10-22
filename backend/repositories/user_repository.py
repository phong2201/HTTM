from sqlalchemy.orm import Session
from models.user_model import User
from schemas.user_schema import UserCreate
from core.security import get_password_hash


def get_user_by_username(db: Session, username: str) -> User | None:
    """Tìm user theo username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Tìm user theo email"""
    return db.query(User).filter(User.email == email).first()


# def get_user_by_id(db: Session, user_id) -> User | None:
#     """Tìm user theo id"""
#     return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Tạo user mới và lưu vào DB"""
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        gender=user_in.gender,
        age=user_in.age,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user_role(db, username, role_id) -> User | None:
    user = get_user_by_username(db, username)
    if user:
        user.role_id = role_id
        db.commit()
        db.refresh(user)
    return user
