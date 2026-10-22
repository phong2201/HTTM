import uuid
from sqlalchemy import Column, TIMESTAMP, ForeignKey, func, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum


class InteractionType(int, PyEnum):
    VIEWED = 1
    ADDED_TO_CART = 2
    REMOVED_FROM_CART = 3
    ADDED_TO_WISHLIST = 4
    REMOVED_FROM_WISHLIST = 5
    PURCHASED = 6


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="user_interactions")

    def __repr__(self):
        return f"<Interaction(user_id={self.user_id!r}, product_id={self.product_id!r}, type={self.interaction_type})>"
