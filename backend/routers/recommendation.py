from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services import recommendation_service
from typing import List
from uuid import UUID
from schemas.recommendation_schema import UserRecommendationResponse

router = APIRouter(prefix="/predict", tags=["Recommendation"])

@router.get("/{user_id}", response_model=List[UserRecommendationResponse])
async def predict_user_recommendations(
    user_id: UUID,
    k: int = 10,
    db: Session = Depends(get_db)
):
    """
    Gợi ý Random Forest tính sẵn cho user, sắp xếp lại theo hành vi trong phiên.
    """
    return await recommendation_service.get_recommendations_for_user(user_id, k, db)
