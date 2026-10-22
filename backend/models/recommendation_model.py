import uuid
from sqlalchemy import Column, Float, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base

class UserRecommendation(Base):
    __tablename__ = "user_recommendations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    version_id = Column(PG_UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
