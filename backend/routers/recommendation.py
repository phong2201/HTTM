from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import recommendation_service
from schemas.product_schema import ProductResponse
from models.user_model import User
from typing import List
from uuid import UUID
from schemas.recommendation_schema import UserRecommendationResponse
from schemas.recommendation_schema import PastRecommendationResponse

router = APIRouter(prefix="/predict", tags=["Recommendation"])

@router.get("/{user_id}", response_model=List[UserRecommendationResponse])
async def predict_user_recommendations(
    user_id: UUID,
    k: int = 10,
    db: Session = Depends(get_db)
):
    """
    API dự đoán sản phẩm gợi ý dựa trên giỏ hàng và wishlist của User.
    """
    return await recommendation_service.get_recommendations_for_user(user_id, k, db)


@router.get("/history/{user_id}/{version_id}", response_model=List[PastRecommendationResponse]) # ĐỔI Ở ĐÂY
async def get_recommendation_history(
    user_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db)
):
    """
    API lấy lại lịch sử gợi ý. 
    """
    return await recommendation_service.get_product_user_recommendations(user_id, version_id, db)


@router.get("/similar/{product_id}/{version_id}", response_model=List[UserRecommendationResponse])
async def get_similar_products(
    product_id: UUID,
    version_id: UUID,
    k: int = 10,
    db: Session = Depends(get_db)
):
    """
    API truy vấn danh sách gợi ý từ Database dựa trên Product ID và Version ID.
    Trả về tất cả các bản ghi trong bảng user_recommendations khớp với điều kiện lọc.
    """
    return await recommendation_service.get_products_recommendation(product_id=product_id, version_id=version_id, k=k, db=db)