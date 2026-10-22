"""Tạo dữ liệu hoạt động DEMO cho tài khoản Buyer: lượt xem, wishlist, giỏ hàng, đơn hàng, đánh giá.

    cd backend
    python scripts/seed_demo_activity.py              # tạo thêm 4 buyer demo + hoạt động cho mọi Buyer
    python scripts/seed_demo_activity.py --buyers 0   # chỉ tạo hoạt động cho các Buyer đang có
    python scripts/seed_demo_activity.py --clear      # xóa sạch mọi thứ script này đã tạo

Đây là dữ liệu giả để trình diễn web (Wishlist, Lịch sử đơn, Dashboard, gợi ý theo hành vi).
Sản phẩm được chọn theo "gu" của từng tài khoản (danh mục/loại trong gợi ý Random Forest của họ) để trông hợp lý.
Mọi dòng tạo ra được ghi vào scripts/.demo_seed.json → --clear xóa đúng những dòng đó, không đụng dữ liệu thật.
Đơn demo có ghi chú bắt đầu bằng "[demo]".
"""
import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from core.security import get_password_hash  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
import models  # noqa: E402,F401
from models import hm_model, model_ai_model, recommendation_model, feedback_model, interaction_model  # noqa: E402,F401
from models.cart_model import Cart  # noqa: E402
from models.feedback_model import Feedback  # noqa: E402
from models.interaction_model import Interaction, InteractionType  # noqa: E402
from models.model_ai_model import ModelVersion  # noqa: E402
from models.order_model import Order, OrderItem, OrderStatus  # noqa: E402
from models.product_model import Product  # noqa: E402
from models.recommendation_model import UserRecommendation  # noqa: E402
from models.user_model import Role, User  # noqa: E402
from models.wishlist_model import Wishlist  # noqa: E402

LEDGER = Path(__file__).with_name(".demo_seed.json")
PASSWORD = "123456"
NAMES = ["an", "binh", "chi", "dung", "giang", "huong", "khanh", "linh", "minh", "ngoc", "phuong", "quan"]
ADDRESSES = ["12 Lê Lợi, Quận 1, TP. Hồ Chí Minh", "45 Cầu Giấy, Cầu Giấy, Hà Nội",
             "8 Bạch Đằng, Hải Châu, Đà Nẵng", "220 Nguyễn Văn Cừ, Ninh Kiều, Cần Thơ"]


def load_ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"users": [], "orders": [], "wishlists": [], "carts": [], "feedbacks": [], "interactions": []}


def ago(days: float) -> datetime:
    """Thời điểm UTC (không kèm múi giờ — giống server_default của DB) cách hiện tại `days` ngày."""
    return datetime.utcnow() - timedelta(days=days, minutes=random.randint(0, 600))


def clear():
    ledger = load_ledger()
    db = SessionLocal()
    try:
        for model, key, col in [(Feedback, "feedbacks", Feedback.id), (Interaction, "interactions", Interaction.id),
                                (Wishlist, "wishlists", Wishlist.id), (Cart, "carts", Cart.id),
                                (Order, "orders", Order.id)]:
            ids = [UUID(i) if key != "carts" else int(i) for i in ledger[key]]
            if ids:
                for row in db.query(model).filter(col.in_(ids)):
                    db.delete(row)   # Order → cascade xóa order_items
            print(f"  {key}: xóa {len(ids)}")
        user_ids = [UUID(i) for i in ledger["users"]]
        if user_ids:
            db.query(UserRecommendation).filter(UserRecommendation.user_id.in_(user_ids)).delete(synchronize_session=False)
            # SQLite không bật khóa ngoại → tự xóa liên kết customer_id của user demo
            db.query(hm_model.UserCustomerLink).filter(hm_model.UserCustomerLink.user_id.in_(user_ids)).delete(synchronize_session=False)
            for user in db.query(User).filter(User.id.in_(user_ids)):
                db.delete(user)
        print(f"  users demo: xóa {len(user_ids)}")
        # Doanh số tổng hợp / sổ đã chốt có thể đã gồm đơn demo → xóa để sales_service tổng hợp lại từ đơn thật
        from models.sales_model import SalesDaily, SalesPeriod
        db.query(SalesDaily).delete()
        db.query(SalesPeriod).delete()
        print("  sales_daily / sales_periods: xóa để tổng hợp lại")
        db.commit()
    finally:
        db.close()
    LEDGER.unlink(missing_ok=True)


def create_buyers(n: int, ledger: dict) -> int:
    db = SessionLocal()
    created = 0
    try:
        existing = {u for (u,) in db.query(User.username)}
        for name in NAMES:
            if created >= n:
                break
            username = f"demo_{name}"
            if username in existing:
                continue
            user = User(username=username, email=f"{username}@hub.local", password_hash=get_password_hash(PASSWORD),
                        role_id=Role.BUYER, gender=random.choice(["female", "female", "male"]), age=random.randint(18, 50))
            db.add(user)
            db.flush()
            ledger["users"].append(str(user.id))
            created += 1
        db.commit()
    finally:
        db.close()
    return created


def link_new_buyers():
    """Gán customer_id H&M + gợi ý cho Buyer mới bằng cách nạp lại run đang dùng."""
    from services.hm_pipeline_service import pipeline
    run_id = pipeline.state["active_run_id"]
    if run_id:
        print("  " + pipeline.import_run(run_id, force=True)["message"])
    else:
        print("  Chưa có run nào — Buyer mới chưa có gợi ý (hãy bấm Train AI)")


def taste_of(db, user: User) -> tuple[list[str], list[str]]:
    """Danh mục + loại sản phẩm hay xuất hiện trong gợi ý của khách (gu thật từ model)."""
    version = db.query(ModelVersion).filter(ModelVersion.is_active.is_(True)).first()
    groups, types = Counter(), Counter()
    if version:
        rows = (db.query(Product.index_group_name, Product.product_type_name)
                  .join(UserRecommendation, UserRecommendation.product_id == Product.id)
                  .filter(UserRecommendation.user_id == user.id, UserRecommendation.version_id == version.id))
        for g, t in rows:
            groups[g] += 1
            types[t] += 1
    return [g for g, _ in groups.most_common(2)], [t for t, _ in types.most_common(4)]


def pick(products: list[Product], k: int, exclude: set) -> list[Product]:
    pool = [p for p in products if p.id not in exclude]
    weights = [(p.sales_last_week or 0) + 1 for p in pool]
    chosen = []
    while pool and len(chosen) < k:
        p = random.choices(pool, weights=weights)[0]
        i = pool.index(p)
        pool.pop(i)
        weights.pop(i)
        chosen.append(p)
    return chosen


def seed_user(db, user: User, catalog: list[Product], ledger: dict) -> dict:
    groups, types = taste_of(db, user)
    if not groups:
        groups = [random.choice(sorted({p.index_group_name for p in catalog if p.index_group_name}))]
    liked = [p for p in catalog if p.index_group_name in groups and (not types or p.product_type_name in types)]
    nearby = [p for p in catalog if p.index_group_name in groups]
    pool = liked if len(liked) >= 30 else nearby
    used: set = set()

    viewed = pick(pool, random.randint(10, 18), used)
    for p in viewed:
        it = Interaction(user_id=user.id, product_id=p.id, interaction_type=InteractionType.VIEWED, created_at=ago(random.uniform(0, 14)))
        db.add(it)
        db.flush()
        ledger["interactions"].append(str(it.id))

    has_wish = {pid for (pid,) in db.query(Wishlist.product_id).filter(Wishlist.user_id == user.id)}
    wish = pick(viewed, random.randint(3, 6), has_wish)
    for p in wish:
        when = ago(random.uniform(0, 10))
        w = Wishlist(user_id=user.id, product_id=p.id, created_at=when)
        it = Interaction(user_id=user.id, product_id=p.id, interaction_type=InteractionType.ADDED_TO_WISHLIST, created_at=when)
        db.add_all([w, it])
        db.flush()
        ledger["wishlists"].append(str(w.id))
        ledger["interactions"].append(str(it.id))

    has_cart = {pid for (pid,) in db.query(Cart.product_id).filter(Cart.user_id == user.id)}
    cart = pick(pool, random.randint(1, 2), has_cart | {p.id for p in wish})
    for p in cart:
        when = ago(random.uniform(0, 3))
        c = Cart(user_id=user.id, product_id=p.id, quantity=1, created_at=when)
        it = Interaction(user_id=user.id, product_id=p.id, interaction_type=InteractionType.ADDED_TO_CART, created_at=when)
        db.add_all([c, it])
        db.flush()
        ledger["carts"].append(str(c.id))
        ledger["interactions"].append(str(it.id))

    n_orders = random.randint(2, 4)
    ages = sorted(random.uniform(0.5, 60) for _ in range(n_orders))
    for idx, age in enumerate(ages):
        items = pick(pool, random.randint(1, 3), used)
        used |= {p.id for p in items}
        if age > 10:
            status = OrderStatus.CANCELLED if idx == len(ages) - 1 and random.random() < 0.3 else OrderStatus.COMPLETED
        elif age > 3:
            status = OrderStatus.DELIVERING
        else:
            status = OrderStatus.PENDING
        when = ago(age)
        order = Order(user_id=user.id, order_date=when, status=status, total_amount=0,
                      note=f"[demo] {user.username} | {random.choice(ADDRESSES)} | cod")
        db.add(order)
        db.flush()
        total = 0.0
        for p in items:
            qty = random.choice([1, 1, 1, 2])
            db.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, unit_price=p.price, subtotal=p.price * qty))
            total += p.price * qty
            if status == OrderStatus.COMPLETED and random.random() < 0.7:
                fb = Feedback(user_id=user.id, product_id=p.id, rank=random.choice([5, 5, 4, 4, 4, 3, 2]),
                              created_at=when + timedelta(days=random.uniform(2, 6)))
                db.add(fb)
                db.flush()
                ledger["feedbacks"].append(str(fb.id))
        order.total_amount = total
        ledger["orders"].append(str(order.id))
    return {"views": len(viewed), "wishlist": len(wish), "cart": len(cart), "orders": n_orders, "taste": groups + types[:2]}


def main():
    parser = argparse.ArgumentParser(description="Tạo dữ liệu hoạt động demo cho Buyer")
    parser.add_argument("--buyers", type=int, default=4, help="số tài khoản Buyer demo tạo thêm (mật khẩu 123456)")
    parser.add_argument("--clear", action="store_true", help="xóa mọi dữ liệu do script này tạo")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    Base.metadata.create_all(bind=engine)
    if args.clear:
        clear()
        print("Đã xóa dữ liệu demo.")
        return

    random.seed(args.seed)
    ledger = load_ledger()
    n = create_buyers(args.buyers, ledger)
    LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"Tạo {n} Buyer demo (mật khẩu {PASSWORD})")
    if n:
        link_new_buyers()

    db = SessionLocal()
    try:
        catalog = db.query(Product).filter(Product.is_active.is_(True), Product.article_id.isnot(None)).all()
        if not catalog:
            sys.exit("Chưa có sản phẩm H&M — hãy chạy pipeline trước.")
        for user in db.query(User).filter(User.role_id == Role.BUYER).order_by(User.created_at):
            stats = seed_user(db, user, catalog, ledger)
            print(f"  {user.username:<16} xem {stats['views']:>2} · wishlist {stats['wishlist']} · giỏ {stats['cart']} "
                  f"· đơn {stats['orders']} · gu: {', '.join(filter(None, stats['taste']))}")
        db.commit()
    finally:
        db.close()
    LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"Xong. Ghi lại các dòng đã tạo ở {LEDGER.name} (xóa bằng --clear).")


if __name__ == "__main__":
    main()
