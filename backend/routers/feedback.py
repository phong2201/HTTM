from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.feedback_schema import FeedbackResponse, FeedbackCreate, FeedbackUpdate
from services import feedback_service
from typing import List
from uuid import UUID

router = APIRouter(prefix="/feedback", tags=["Product Feedback"])

@router.post("/{user_id}", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    user_id: UUID, 
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    API gửi đánh giá sản phẩm (1-5 sao).
    Nếu đã đánh giá rồi, hệ thống sẽ cập nhật lại điểm mới.
    """
    # Sử dụng trực tiếp user_id từ tham số thay vì current_user.id
    return await feedback_service.submit_feedback_logic(
        user_id, 
        feedback_in.product_id, 
        feedback_in.rank, 
        db
    )


@router.get("/user/{user_id}", response_model=List[FeedbackResponse])
async def get_feedbacks_by_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Lấy toàn bộ lịch sử đánh giá của một User cụ thể"""
    return await feedback_service.get_user_feedbacks_logic(user_id, db)


@router.get("/product/{product_id}", response_model=List[FeedbackResponse])
async def get_feedbacks_by_product(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Lấy toàn bộ các đánh giá của một sản phẩm cụ thể"""
    return await feedback_service.get_product_feedbacks_logic(product_id, db)


@router.put("/{user_id}/{product_id}", response_model=FeedbackResponse)
async def update_feedback(
    user_id: UUID,
    product_id: UUID,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(get_db)
):
    """API cập nhật số sao (rank) cho một đánh giá đã tồn tại."""
    return await feedback_service.update_feedback_logic(user_id, product_id, feedback_in.rank, db)


@router.delete("/{user_id}/{product_id}")
async def delete_feedback(
    user_id: UUID,
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """API xóa vĩnh viễn một đánh giá."""
    return await feedback_service.delete_feedback_logic(user_id, product_id, db)