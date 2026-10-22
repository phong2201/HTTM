# models/ai_model.py
import uuid

from sqlalchemy import Column, Integer, String, Boolean, Float, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base
from sqlalchemy.dialects.postgresql import JSONB

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_tag = Column(String(50), unique=True, nullable=False)
    image_feat_path = Column(String(500))
    text_feat_path = Column(String(500))
    meta_feat_path = Column(String(500))
    gnn_emb_path = Column(String(500))
    model_weights_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    product_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class EDAReport(Base):
    __tablename__ = "eda_reports"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    eda_type = Column(String(20)) # 'original' hoặc 'normalized'
    version_id = Column(PG_UUID(as_uuid=True), ForeignKey("model_versions.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    report_files = Column(JSONB)