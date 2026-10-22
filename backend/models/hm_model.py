from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base


class UserCustomerLink(Base):
    """Liên kết tài khoản Buyer với một customer_id của dataset H&M (customers.csv)."""
    __tablename__ = "user_customer_links"

    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    customer_id = Column(String(64), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
