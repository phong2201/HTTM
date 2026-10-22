from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from models.recommendation_model import UserRecommendation
from sqlalchemy import desc

def bulk_create_recommendations(db: Session, recommendations: List[UserRecommendation]):
    """Lưu danh sách gợi ý vào database theo lô (batch)"""
    db.bulk_save_objects(recommendations)
    db.commit()


def get_recommendations_by_product_ids(db: Session, product_ids: List[UUID], version_id: UUID, limit: int):
    """Truy vấn các sản phẩm tương đồng dựa trên danh sách ID sản phẩm đầu vào"""
    return db.query(UserRecommendation)\
        .filter(UserRecommendation.product_id.in_(product_ids))\
        .filter(UserRecommendation.version_id == version_id)\
        .order_by(desc(UserRecommendation.score))\
        .limit(limit)\
        .all()


def delete_recommendations_by_version(db: Session, version_id: UUID):
    """Xóa các gợi ý cũ của một phiên bản nếu cần train lại"""
    db.query(UserRecommendation).filter(UserRecommendation.version_id == version_id).delete()
    db.commit()


def save_user_recommendations(db: Session, recommendations: List[UserRecommendation]):
    db.bulk_save_objects(recommendations)
    db.commit()


def get_recommendations_by_user_and_version(db: Session, user_id: UUID, version_id: UUID):
    """Truy vấn lịch sử gợi ý của User theo phiên bản Model"""
    return db.query(UserRecommendation).filter(
        UserRecommendation.user_id == user_id,
        UserRecommendation.version_id == version_id
    ).all()


def delete_recommendations_by_user_and_version(db: Session, user_id: UUID, version_id: UUID):
    """Xóa các gợi ý cũ của một User cụ thể trong một phiên bản nhất định"""
    db.query(UserRecommendation).filter(
        UserRecommendation.user_id == user_id,
        UserRecommendation.version_id == version_id
    ).delete()
    db.commit()