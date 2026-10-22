from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from models.interaction_model import Interaction, InteractionType
import repositories.feedback_repository as feedback_repo
from models.user_model import User
from models.product_model import Product
from models.feedback_model import Feedback

async def submit_feedback_logic(user_id: UUID, product_id: UUID, rank: int, db: Session):
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Người dùng với ID {user_id} không tồn tại."
        )

    product_exists = db.query(Product).filter(Product.id == product_id).first()
    if not product_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với ID {product_id} không tồn tại."
        )

    existing_feedback = db.query(Feedback).filter(
        Feedback.user_id == user_id, 
        Feedback.product_id == product_id
    ).first()
    
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn đã đánh giá sản phẩm này rồi. Mỗi người dùng chỉ được đánh giá một lần."
        )

    feedback = feedback_repo.create_or_update_feedback(db, user_id, product_id, rank)
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Lỗi hệ thống: Không thể lưu đánh giá."
        )

    interaction = Interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=InteractionType.VIEWED
    )
    db.add(interaction)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi ghi nhận tương tác vào hệ thống."
        )

    return feedback


async def get_user_feedbacks_logic(user_id: UUID, db: Session):
    """Logic lấy danh sách đánh giá của người dùng với bước check tồn tại"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Người dùng với ID {user_id} không tồn tại"
        )
    
    return feedback_repo.get_feedbacks_by_user(db, user_id)


async def get_product_feedbacks_logic(product_id: UUID, db: Session):
    """Logic lấy danh sách đánh giá của sản phẩm với bước check tồn tại"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )
    
    return feedback_repo.get_feedbacks_by_product(db, product_id)


async def update_feedback_logic(user_id: UUID, product_id: UUID, new_rank: int, db: Session):
    feedback = feedback_repo.update_feedback_rank(db, user_id, product_id, new_rank)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy đánh giá để cập nhật"
        )
    return feedback


async def delete_feedback_logic(user_id: UUID, product_id: UUID, db: Session):
    success = feedback_repo.delete_feedback(db, user_id, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy đánh giá để xóa"
        )
    return {"message": "Xóa đánh giá thành công"}