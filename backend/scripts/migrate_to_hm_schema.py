"""Chuyển DB SQLite sang schema products theo cột H&M (một lần).

    cd backend
    python scripts/migrate_to_hm_schema.py

1. Sao lưu file DB → recommendation_system.backup_<thời gian>.db
2. Xóa sản phẩm dataset cũ (Myntra) và mọi dòng trỏ tới chúng (đơn, giỏ, wishlist, feedback, tương tác, gợi ý)
3. Dựng lại bảng products theo models/product_model.py
4. Nạp lại catalog H&M của run đang dùng (giữ nguyên UUID → giỏ/wishlist/gợi ý H&M vẫn hợp lệ),
   giá quy đổi sang VND theo settings.HM_PRICE_TO_VND

Postgres: dựng DB mới từ scripts.sql rồi bấm Train AI / gọi POST /ai/runs/<run_id>/import thay vì chạy script này.
"""
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from core.config import settings  # noqa: E402

DEPENDENTS = ["order_items", "carts", "wishlists", "feedbacks", "interactions", "user_recommendations"]


def main():
    url = settings.DATABASE_URL
    if not url.startswith("sqlite:///"):
        sys.exit("Script chỉ dành cho SQLite. Postgres: dựng từ scripts.sql rồi nạp lại run.")
    db_path = (BACKEND / url.removeprefix("sqlite:///")).resolve() if not Path(url.removeprefix("sqlite:///")).is_absolute() \
        else Path(url.removeprefix("sqlite:///"))

    con = sqlite3.connect(db_path)
    columns = {row[1] for row in con.execute("PRAGMA table_info(products)")}
    if "article_id" in columns:
        con.close()
        sys.exit("Bảng products đã theo schema H&M — không cần chuyển.")

    backup = db_path.with_name(f"{db_path.stem}.backup_{datetime.now():%Y%m%d_%H%M%S}{db_path.suffix}")
    shutil.copyfile(db_path, backup)
    print(f"Đã sao lưu: {backup.name}")

    con.row_factory = sqlite3.Row
    old_hm = [dict(r) for r in con.execute("SELECT * FROM products WHERE cross_links LIKE 'hm:%'")]
    con.row_factory = None
    hm_ids = [r["id"] for r in old_hm]
    total = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"Sản phẩm: {total} · H&M giữ lại: {len(hm_ids)} · dataset cũ xóa: {total - len(hm_ids)}")

    with con:
        con.execute("CREATE TEMP TABLE keep(id PRIMARY KEY)")
        con.executemany("INSERT INTO keep VALUES (?)", [(i,) for i in hm_ids])
        for table in DEPENDENTS:
            n = con.execute(f"DELETE FROM {table} WHERE product_id NOT IN (SELECT id FROM keep)").rowcount
            print(f"  {table}: xóa {n} dòng trỏ tới sản phẩm cũ")
        n = con.execute("DELETE FROM orders WHERE id NOT IN (SELECT DISTINCT order_id FROM order_items)").rowcount
        print(f"  orders: xóa {n} đơn không còn sản phẩm")
        con.execute("DROP TABLE products")
    con.close()

    # Tạo lại bảng theo model mới rồi nạp catalog H&M
    from database import Base, SessionLocal, engine
    import models  # noqa: F401
    from models import hm_model, model_ai_model, recommendation_model, feedback_model, interaction_model  # noqa: F401
    from services.hm_pipeline_service import RUNS_DIR, pipeline

    from models.product_model import Product
    from services.hm_pipeline_service import product_id_for, to_vnd

    Base.metadata.create_all(bind=engine)
    # Chuyển nguyên mọi sản phẩm H&M cũ (kể cả món không còn trong catalog mới) sang cột H&M
    db = SessionLocal()
    try:
        for r in old_hm:
            aid = r["cross_links"][3:]
            db.add(Product(
                id=product_id_for(aid), article_id=aid, product_code=aid[:7],
                prod_name=r["product_display_name"], product_type_name=r["article_type"],
                product_group_name=r["sub_category"], colour_group_name=r["base_colour"],
                graphical_appearance_name=r["usage"], index_group_name=r["master_category"],
                detail_desc=r["description"], price=to_vnd(r["price"] or 0), image_url=r["image_url"],
                quantity_in_stock=r["quantity_in_stock"] or 0, is_active=bool(r["is_active"]),
            ))
        db.commit()
    finally:
        db.close()
    print(f"Đã chuyển {len(old_hm)} sản phẩm H&M sang cột mới")

    run_id = pipeline.state["active_run_id"]
    if not run_id:
        print("Chưa có run nào được ghi — bảng products đang trống, hãy bấm Train AI.")
        return
    db = SessionLocal()
    try:
        n = pipeline._import_catalog(db, RUNS_DIR / run_id)
        db.commit()
    finally:
        db.close()
    print(f"Đã cập nhật {n} sản phẩm theo catalog {run_id} (giá × {settings.HM_PRICE_TO_VND:,.0f} → VND, lượt bán tuần)")


if __name__ == "__main__":
    main()
