from uuid import UUID

from sqlalchemy.orm import Session
from models.feedback_model import Feedback

def create_or_update_feedback(db: Session, user_id: str, product_id: str, rank: int):
    # Kiểm tra xem user đã feedback sản phẩm này chưa dựa trên ID dạng chuỗi
    existing_feedback = db.query(Feedback).filter(
        Feedback.user_id == user_id, 
        Feedback.product_id == product_id
    ).first()

    if existing_feedback:
        existing_feedback.rank = rank
        db.commit()
        db.refresh(existing_feedback)
        return existing_feedback

    # Tạo feedback mới với user_id và product_id là string
    new_feedback = Feedback(user_id=user_id, product_id=product_id, rank=rank)
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


def get_feedback_by_user_and_product(db: Session, user_id: str, product_id: str):
    return db.query(Feedback).filter(
        Feedback.user_id == user_id, 
        Feedback.product_id == product_id
    ).first()


def get_feedbacks_by_user(db: Session, user_id: str):
    """Lấy danh sách tất cả đánh giá của một người dùng"""
    return db.query(Feedback).filter(Feedback.user_id == user_id).all()


def get_feedbacks_by_product(db: Session, product_id: str):
    """Lấy danh sách tất cả đánh giá của một sản phẩm"""
    return db.query(Feedback).filter(Feedback.product_id == product_id).all()


def update_feedback_rank(db: Session, user_id: UUID, product_id: UUID, new_rank: int):
    feedback = db.query(Feedback).filter(
        Feedback.user_id == user_id, 
        Feedback.product_id == product_id
    ).first()
    
    if feedback:
        feedback.rank = new_rank
        db.commit()
        db.refresh(feedback)
    return feedback


def delete_feedback(db: Session, user_id: UUID, product_id: UUID):
    feedback = db.query(Feedback).filter(
        Feedback.user_id == user_id, 
        Feedback.product_id == product_id
    ).first()
    
    if feedback:
        db.delete(feedback)
        db.commit()
        return True
    return False