from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from .base_schema import ICTBaseModel

class FeedbackCreate(BaseModel):
    product_id: UUID
    rank: int = Field(..., ge=1, le=5, description="Rank phải từ 1 đến 5")

class FeedbackResponse(ICTBaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    rank: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FeedbackUpdate(BaseModel):
    rank: int = Field(..., ge=1, le=5, description="Rank mới phải từ 1 đến 5")