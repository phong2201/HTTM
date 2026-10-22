"""Tổng hợp doanh số: dữ liệu nóng (hôm nay, tính trực tiếp) tách khỏi dữ liệu thống kê (bảng tổng hợp).

- sales_daily: mỗi ngày một dòng. Ngày đã qua được tổng hợp một lần; 7 ngày gần nhất tính lại mỗi lần
  cập nhật để bắt kịp đơn đổi trạng thái muộn (giao xong, hủy...).
- sales_periods: hết tháng / năm thì chốt sổ một lần (doanh thu, số đơn, top sản phẩm) → kỳ mới tính lại từ 0.
  Đơn gốc trong bảng orders vẫn giữ nguyên (lịch sử đơn, đánh giá, đối soát).
Ngày tính theo giờ Việt Nam (UTC+7); orders.order_date lưu UTC.
"""
from __future__ import annotations

import json
import threading
import time
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import SessionLocal
from models.order_model import Order, OrderItem, OrderStatus
from models.product_model import Product
from models.sales_model import SalesDaily, SalesPeriod

VN = timezone(timedelta(hours=7))
RECOMPUTE_DAYS = 7
REFRESH_SECONDS = 600


def today_vn() -> date:
    return datetime.now(VN).date()


def _utc_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    """[start, end) theo giờ VN → mốc UTC không kèm múi giờ (giống cách DB lưu order_date)."""
    to_utc = lambda d: datetime(d.year, d.month, d.day, tzinfo=VN).astimezone(timezone.utc).replace(tzinfo=None)  # noqa: E731
    return to_utc(start), to_utc(end)


def aggregate(db: Session, start: date, end: date) -> dict:
    """Số liệu trực tiếp từ orders trong [start, end)."""
    lo, hi = _utc_bounds(start, end)
    in_range = (Order.order_date >= lo, Order.order_date < hi)
    valid = db.query(func.count(Order.id), func.coalesce(func.sum(Order.total_amount), 0), func.count(func.distinct(Order.user_id))) \
              .filter(*in_range, Order.status != OrderStatus.CANCELLED).one()
    cancelled = db.query(func.count(Order.id)).filter(*in_range, Order.status == OrderStatus.CANCELLED).scalar() or 0
    items = db.query(func.coalesce(func.sum(OrderItem.quantity), 0)).join(Order) \
              .filter(*in_range, Order.status != OrderStatus.CANCELLED).scalar() or 0
    return {"orders": int(valid[0] or 0), "revenue": float(valid[1] or 0), "customers": int(valid[2] or 0),
            "cancelled_orders": int(cancelled), "items": int(items)}


def top_products(db: Session, start: date, end: date, limit: int = 5) -> list[dict]:
    lo, hi = _utc_bounds(start, end)
    rows = (db.query(Product.id, Product.prod_name, func.sum(OrderItem.quantity), func.sum(OrderItem.subtotal))
              .join(OrderItem, OrderItem.product_id == Product.id).join(Order, Order.id == OrderItem.order_id)
              .filter(Order.order_date >= lo, Order.order_date < hi, Order.status != OrderStatus.CANCELLED)
              .group_by(Product.id, Product.prod_name)
              .order_by(func.sum(OrderItem.subtotal).desc()).limit(limit).all())
    return [{"id": str(pid), "name": name, "sold": int(sold or 0), "revenue": float(rev or 0)} for pid, name, sold, rev in rows]


def rollup_day(db: Session, day: date):
    stats = aggregate(db, day, day + timedelta(days=1))
    row = db.get(SalesDaily, day) or SalesDaily(day=day)
    for key, value in stats.items():
        setattr(row, key, value)
    db.add(row)


def _month_range(key: str) -> tuple[date, date]:
    y, m = (int(x) for x in key.split("-"))
    start = date(y, m, 1)
    return start, date(y + (m == 12), m % 12 + 1, 1)


def _year_range(key: str) -> tuple[date, date]:
    y = int(key)
    return date(y, 1, 1), date(y + 1, 1, 1)


def close_period(db: Session, period_type: str, key: str):
    start, end = _month_range(key) if period_type == "month" else _year_range(key)
    sums = db.query(func.coalesce(func.sum(SalesDaily.orders), 0), func.coalesce(func.sum(SalesDaily.cancelled_orders), 0),
                    func.coalesce(func.sum(SalesDaily.items), 0), func.coalesce(func.sum(SalesDaily.revenue), 0)) \
             .filter(SalesDaily.day >= start, SalesDaily.day < end).one()
    customers = aggregate(db, start, end)["customers"]   # khách khác nhau trong kỳ (không cộng được từ từng ngày)
    db.add(SalesPeriod(period_type=period_type, period_key=key, orders=int(sums[0]), cancelled_orders=int(sums[1]),
                       items=int(sums[2]), revenue=float(sums[3]), customers=customers,
                       top_products=json.dumps(top_products(db, start, end), ensure_ascii=False)))


def refresh(db: Session):
    """Tổng hợp các ngày còn thiếu tới hôm qua, tính lại 7 ngày gần nhất, chốt các tháng/năm đã kết thúc."""
    today = today_vn()
    first_order = db.query(func.min(Order.order_date)).scalar()
    if first_order is None:
        return
    first_day = first_order.replace(tzinfo=timezone.utc).astimezone(VN).date() if first_order.tzinfo is None \
        else first_order.astimezone(VN).date()
    last_rolled = db.query(func.max(SalesDaily.day)).scalar()
    start = min(first_day if last_rolled is None else last_rolled + timedelta(days=1), today - timedelta(days=RECOMPUTE_DAYS))
    start = max(start, first_day)
    day = start
    while day < today:
        rollup_day(db, day)
        day += timedelta(days=1)
    db.flush()

    closed = {(p.period_type, p.period_key) for p in db.query(SalesPeriod.period_type, SalesPeriod.period_key)}
    month = date(first_day.year, first_day.month, 1)
    this_month = date(today.year, today.month, 1)
    while month < this_month:
        key = f"{month:%Y-%m}"
        if ("month", key) not in closed:
            close_period(db, "month", key)
        month = _month_range(key)[1]
    for year in range(first_day.year, today.year):
        if ("year", str(year)) not in closed:
            close_period(db, "year", str(year))
    db.commit()


def summary(db: Session) -> dict:
    """Hôm nay / tháng này / năm nay (tính tới hiện tại) + kỳ trước để so sánh + các tháng đã chốt."""
    refresh(db)
    today = today_vn()
    month_start, year_start = date(today.year, today.month, 1), date(today.year, 1, 1)

    def period(start: date, end: date) -> dict:
        # Ngày đã qua đọc từ bảng tổng hợp, riêng hôm nay tính trực tiếp
        past = db.query(func.coalesce(func.sum(SalesDaily.orders), 0), func.coalesce(func.sum(SalesDaily.items), 0),
                        func.coalesce(func.sum(SalesDaily.revenue), 0), func.coalesce(func.sum(SalesDaily.cancelled_orders), 0)) \
                 .filter(SalesDaily.day >= start, SalesDaily.day < min(end, today)).one()
        live = aggregate(db, today, today + timedelta(days=1)) if start <= today < end else None
        return {
            "orders": int(past[0]) + (live["orders"] if live else 0),
            "items": int(past[1]) + (live["items"] if live else 0),
            "revenue": float(past[2]) + (live["revenue"] if live else 0),
            "cancelled_orders": int(past[3]) + (live["cancelled_orders"] if live else 0),
            "customers": aggregate(db, start, min(end, today + timedelta(days=1)))["customers"],
        }

    def closed(period_type: str, key: str) -> dict | None:
        p = db.query(SalesPeriod).filter_by(period_type=period_type, period_key=key).first()
        return _period_dict(p) if p else None

    prev_month_key = f"{(month_start - timedelta(days=1)):%Y-%m}"
    months = db.query(SalesPeriod).filter_by(period_type="month").order_by(SalesPeriod.period_key.desc()).limit(12).all()
    years = db.query(SalesPeriod).filter_by(period_type="year").order_by(SalesPeriod.period_key.desc()).all()
    return {
        "today": {"key": today.isoformat(), **aggregate(db, today, today + timedelta(days=1))},
        "month": {"key": f"{today:%Y-%m}", **period(month_start, _month_range(f"{today:%Y-%m}")[1]),
                  "top_products": top_products(db, month_start, today + timedelta(days=1))},
        "year": {"key": str(today.year), **period(year_start, date(today.year + 1, 1, 1))},
        "previous_month": closed("month", prev_month_key),
        "previous_year": closed("year", str(today.year - 1)),
        "closed_months": [_period_dict(p) for p in reversed(months)],
        "closed_years": [_period_dict(p) for p in reversed(years)],
    }


def _period_dict(p: SalesPeriod) -> dict:
    return {"key": p.period_key, "orders": p.orders, "cancelled_orders": p.cancelled_orders, "items": p.items,
            "customers": p.customers, "revenue": p.revenue, "top_products": json.loads(p.top_products or "[]"),
            "closed_at": p.closed_at}


def start_scheduler():
    """Cập nhật bảng tổng hợp & chốt sổ định kỳ (rẻ: chỉ đụng các ngày gần nhất)."""
    def loop():
        while True:
            db = SessionLocal()
            try:
                refresh(db)
            except Exception as exc:  # noqa: BLE001
                print(f"[sales] {exc}", flush=True)
            finally:
                db.close()
            time.sleep(REFRESH_SECONDS)
    threading.Thread(target=loop, daemon=True, name="sales-rollup").start()
