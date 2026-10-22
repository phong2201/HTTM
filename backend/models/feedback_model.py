import uuid
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    
    # Giá trị từ 1 đến 5
    rank = Column(Integer, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())