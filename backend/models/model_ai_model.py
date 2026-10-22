# models/model_ai_model.py
import uuid

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base

class ModelVersion(Base):
    """Một lần chạy pipeline Random Forest đã nạp vào DB (version_tag = run_id)."""
    __tablename__ = "model_versions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_tag = Column(String(50), unique=True, nullable=False)
    model_weights_path = Column(String(500))  # thư mục data_scientist/runs/<run_id>
    is_active = Column(Boolean, default=True)
    product_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
