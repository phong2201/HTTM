from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user_model import User
from models.product_model import Product
from models.model_ai_model import ModelVersion
from models.recommendation_model import UserRecommendation


async def get_recommendations_for_user(user_id: UUID, k: int, db: Session):
    """Gợi ý = kết quả Random Forest tính sẵn (bảng user_recommendations, ModelVersion active)
    rồi sắp xếp lại theo hành vi gần đây trên web (services/session_rerank.py).

    Chưa có gợi ý và chưa có hành vi nào → trả [] để front-end hiển thị bán chạy (cold start).
    """
    from services.session_rerank import Scored, rerank

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    base: list = []
    active_version = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
    if active_version:
        recs = (db.query(UserRecommendation)
                  .filter(UserRecommendation.user_id == user_id, UserRecommendation.version_id == active_version.id)
                  .order_by(UserRecommendation.rank)
                  .all())
        products = {p.id: p for p in db.query(Product).filter(Product.id.in_([r.product_id for r in recs]))}
        base = [Scored(products[r.product_id], r.score) for r in recs if r.product_id in products]

    ranked = rerank(db, user_id, base, k)
    return [
        {"product_id": s.product.id, "score": round(s.score, 6), "rank": i, "product_details": s.product}
        for i, s in enumerate(ranked, 1)
    ]
