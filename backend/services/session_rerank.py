"""Sắp xếp lại gợi ý theo hành vi gần đây trên web (xem, wishlist, giỏ, mua, đánh giá).

Gợi ý gốc do Random Forest tính sẵn mỗi đêm (bảng user_recommendations). Lớp này chạy lúc gọi /predict:
  - món "giống" món vừa tương tác (cùng product_code > cùng loại & danh mục > cùng nhóm) được cộng điểm,
    tín hiệu mạnh dần: xem < giỏ < wishlist; tín hiệu cũ mờ dần (bán rã HALF_LIFE_DAYS ngày);
  - món đã mua, đã đánh giá ≤ 2 sao bị loại; bỏ wishlist / bỏ giỏ thì trừ điểm.
Nhờ vậy khách cold start (chưa có gợi ý từ model) cũng có gợi ý ngay sau vài lượt xem.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from models.feedback_model import Feedback
from models.interaction_model import Interaction, InteractionType
from models.order_model import Order, OrderItem
from models.product_model import Product

LOOKBACK_DAYS = 30
MAX_EVENTS = 50
HALF_LIFE_DAYS = 3.0
EVENT_WEIGHT = {
    InteractionType.VIEWED: 1.0,
    InteractionType.ADDED_TO_CART: 2.5,
    InteractionType.ADDED_TO_WISHLIST: 3.0,
    InteractionType.REMOVED_FROM_CART: -1.0,
    InteractionType.REMOVED_FROM_WISHLIST: -2.0,
}
SIMILARITY = {"code": 1.0, "type": 0.35, "group": 0.15}
BOOST_SCALE = 0.25          # điểm model ~0–1; 1 lượt wishlist cùng product_code ≈ +0.75
NEIGHBOURS_PER_ANCHOR = 20
MAX_PER_CODE = 1


@dataclass
class Scored:
    product: Product
    score: float


def product_code(p: Product) -> str | None:
    """Cùng product_code = cùng mẫu, khác màu (article_id = product_code + 3 số biến thể)."""
    return p.product_code


def _similarity(a: Product, b: Product) -> float:
    code = product_code(a)
    if code and code == product_code(b):
        return SIMILARITY["code"]
    if a.product_type_name and a.product_type_name == b.product_type_name and a.index_group_name == b.index_group_name:
        return SIMILARITY["type"]
    if a.product_group_name and a.product_group_name == b.product_group_name:
        return SIMILARITY["group"]
    return 0.0


def _age_days(ts: datetime | None, now: datetime) -> float:
    if ts is None:
        return 0.0
    if ts.tzinfo is None:  # SQLite trả về giờ UTC không kèm múi giờ
        ts = ts.replace(tzinfo=timezone.utc)
    return max(0.0, (now - ts).total_seconds() / 86400)


def rerank(db: Session, user_id: UUID, base: list[Scored], k: int) -> list[Scored]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=LOOKBACK_DAYS)

    events = (db.query(Interaction)
                .filter(Interaction.user_id == user_id, Interaction.interaction_type.in_(list(EVENT_WEIGHT)))
                .order_by(Interaction.created_at.desc())
                .limit(MAX_EVENTS).all())
    anchors: dict[UUID, float] = defaultdict(float)
    for e in events:
        age = _age_days(e.created_at, now)
        if age <= LOOKBACK_DAYS:
            anchors[e.product_id] += EVENT_WEIGHT[e.interaction_type] * 0.5 ** (age / HALF_LIFE_DAYS)

    purchased = {pid for (pid,) in db.query(OrderItem.product_id).join(Order).filter(Order.user_id == user_id)}
    disliked = {pid for (pid,) in db.query(Feedback.product_id).filter(Feedback.user_id == user_id, Feedback.rank <= 2)}
    blocked = purchased | disliked

    if not anchors and not blocked:
        return base[:k]

    anchor_products = {p.id: p for p in db.query(Product).filter(Product.id.in_(list(anchors)))} if anchors else {}
    disliked_products = list(db.query(Product).filter(Product.id.in_(list(disliked)))) if disliked else []

    # Ứng viên = gợi ý của model + món giống các món khách vừa quan tâm
    pool: dict[UUID, Scored] = {s.product.id: Scored(s.product, s.score) for s in base}
    for pid, weight in anchors.items():
        anchor = anchor_products.get(pid)
        if anchor is None or weight <= 0:
            continue
        code = product_code(anchor)
        q = db.query(Product).filter(Product.is_active.is_(True), Product.id != anchor.id)
        same_code = q.filter(Product.product_code == code).all() if code else []
        same_type = (q.filter(Product.product_type_name == anchor.product_type_name,
                              Product.index_group_name == anchor.index_group_name)
                      .order_by(Product.sales_last_week.desc())
                      .limit(NEIGHBOURS_PER_ANCHOR).all() if anchor.product_type_name else [])
        for p in same_code + same_type:
            pool.setdefault(p.id, Scored(p, 0.0))

    # Món khách đã cho vào wishlist / giỏ / vừa xem thì không gợi ý lại chính nó
    shown_already = {pid for pid, w in anchors.items() if w > 0}
    max_pop = max((s.product.sales_last_week or 0 for s in pool.values()), default=0) or 1
    results = []
    for item in pool.values():
        if item.product.id in blocked or item.product.id in shown_already or not item.product.is_active:
            continue
        boost = sum(w * _similarity(item.product, anchor_products[pid])
                    for pid, w in anchors.items() if pid in anchor_products)
        penalty = sum(0.5 for d in disliked_products if product_code(d) and product_code(d) == product_code(item.product))
        # Món không có điểm model: phá hòa bằng độ bán chạy tuần (không đụng thứ tự của model)
        tie = 0.02 * (item.product.sales_last_week or 0) / max_pop if item.score == 0 else 0.0
        results.append(Scored(item.product, item.score + BOOST_SCALE * boost - penalty + tie))

    results.sort(key=lambda s: s.score, reverse=True)
    # H&M đặt cùng tên cho các màu của một sản phẩm → tối đa MAX_PER_CODE màu mỗi product_code cho đỡ trùng
    picked, per_code = [], defaultdict(int)
    for s in results:
        code = product_code(s.product) or str(s.product.id)
        if per_code[code] < MAX_PER_CODE:
            per_code[code] += 1
            picked.append(s)
        if len(picked) == k:
            break
    return picked
