from sqlalchemy import Column, Date, Float, Integer, String, Text, TIMESTAMP, UniqueConstraint, func
from database import Base


class SalesDaily(Base):
    """Doanh số tổng hợp theo ngày (giờ Việt Nam) — dashboard đọc bảng này thay vì cộng lại toàn bộ orders."""
    __tablename__ = "sales_daily"

    day = Column(Date, primary_key=True)
    orders = Column(Integer, nullable=False, default=0)
    cancelled_orders = Column(Integer, nullable=False, default=0)
    items = Column(Integer, nullable=False, default=0)
    customers = Column(Integer, nullable=False, default=0)
    revenue = Column(Float, nullable=False, default=0)          # VND, không tính đơn đã hủy
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class SalesPeriod(Base):
    """Sổ đã chốt của một tháng / năm. Hết kỳ → ghi lại một lần, kỳ mới bắt đầu tính từ 0."""
    __tablename__ = "sales_periods"
    __table_args__ = (UniqueConstraint("period_type", "period_key", name="_sales_period_uc"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    period_type = Column(String(5), nullable=False)       # "month" | "year"
    period_key = Column(String(7), nullable=False)        # "2026-10" | "2026"
    orders = Column(Integer, nullable=False, default=0)
    cancelled_orders = Column(Integer, nullable=False, default=0)
    items = Column(Integer, nullable=False, default=0)
    customers = Column(Integer, nullable=False, default=0)
    revenue = Column(Float, nullable=False, default=0)
    top_products = Column(Text, nullable=True)            # JSON: [{id, name, sold, revenue}]
    closed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
