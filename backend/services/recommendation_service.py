import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status

from models.user_model import User
from models.cart_model import Cart
from models.wishlist_model import Wishlist
from models.product_model import Product
from models.model_ai_model import ModelVersion
from models.recommendation_model import UserRecommendation
import repositories.recommendation_repository as rec_repo
from models.recommendation_model import UserRecommendation
from models.feedback_model import Feedback

base_dir = Path(__file__).resolve().parent.parent.parent

def get_product_indices(product_uuids: List[UUID], id_csv_path: Path) -> List[int]:
    """Hàm ánh xạ UUID sản phẩm sang Index trong ma trận embeddings"""
    if not id_csv_path.exists():
        return []
    df_ids = pd.read_csv(id_csv_path)
    indices = df_ids[df_ids['id'].isin([str(u) for u in product_uuids])].index.tolist()
    return indices


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


async def get_product_user_recommendations(user_id: UUID, version_id: UUID, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=404, 
            detail=f"Phiên bản Model với ID {version_id} không tồn tại trong hệ thống"
        )

    past_recs = rec_repo.get_recommendations_by_user_and_version(db, user_id, version_id)
    if not past_recs:
        return []

    product_ids = [rec.product_id for rec in past_recs]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    final_results = []
    for pid in product_ids:
        if pid in product_map:
            final_results.append({
                "product_id": pid,
                "product_details": product_map[pid]
            })

    return final_results


async def get_products_recommendation(product_id: UUID, version_id: UUID, k: int, db: Session):
    target_product = db.query(Product).filter(Product.id == product_id).first()
    if not target_product:
        raise HTTPException(status_code=404, detail=f"Sản phẩm ID {product_id} không tồn tại")

    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail=f"Phiên bản Model ID {version_id} không tồn tại")

    recommendations = db.query(UserRecommendation).filter(
        UserRecommendation.product_id == product_id,
        UserRecommendation.version_id == version_id
    ).limit(k).all()

    if not recommendations:
        return []

    final_response = []
    for rec in recommendations:
        final_response.append({
            "product_id": rec.product_id,
            "score": rec.score,
            "rank": rec.rank,
            "product_details": target_product
        })

    return final_response