import csv
from pathlib import Path
from uuid import UUID

from database import SessionLocal
from models.product_model import Product


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = PROJECT_ROOT / "data_scientist" / "standard_dataset" / "fashion_preprocessed_dataset.csv"
IMAGES_DIR = PROJECT_ROOT / "data_scientist" / "images"
PUBLIC_IMAGE_BASE_URL = "http://localhost:8080/images"


def optional_text(value: str | None) -> str | None:
    value = (value or "").strip()
    if not value or value.lower() in {"nan", "none", "null", "not found", "unknown"}:
        return None
    return value


def optional_float(value: str | None) -> float | None:
    value = optional_text(value)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def optional_int(value: str | None) -> int | None:
    value = optional_float(value)
    return int(value) if value is not None else None


def image_url_for(product_id: str) -> str | None:
    image_path = IMAGES_DIR / f"{product_id}.jpg"
    if image_path.exists():
        return f"{PUBLIC_IMAGE_BASE_URL}/{product_id}.jpg"
    return None


def build_product(row: dict[str, str]) -> Product:
    product_id = str(UUID(row["id"]))
    price = optional_float(row.get("price")) or 0
    discounted_price = optional_float(row.get("discountedPrice"))

    return Product(
        id=UUID(product_id),
        brand_name=optional_text(row.get("brandName")) or "Unknown Brand",
        product_display_name=optional_text(row.get("productDisplayName")) or "Unnamed product",
        image_url=image_url_for(product_id),
        description=optional_text(row.get("description")),
        style_note=optional_text(row.get("style_note")),
        occasion=optional_text(row.get("occasion")),
        cross_links=optional_text(row.get("cross_links")),
        is_active=True,
        gender=gender_from_one_hot(row),
        master_category=optional_text(row.get("masterCategory")),
        sub_category=optional_text(row.get("subCategory")),
        article_type=optional_text(row.get("articleType")),
        base_colour=optional_text(row.get("baseColour")),
        season=season_from_one_hot(row),
        usage=usage_from_one_hot(row),
        price=price,
        discounted_price=discounted_price,
        myntra_rating=optional_float(row.get("myntraRating")),
        fabric=optional_text(row.get("fabric")),
        fit=optional_text(row.get("fit")),
        neck=optional_text(row.get("neck")),
        quantity_in_stock=optional_int(row.get("quantity_in_stock")) or 100,
    )


def gender_from_one_hot(row: dict[str, str]) -> str | None:
    for key, label in [
        ("gen_Men", "Men"),
        ("gen_Women", "Women"),
        ("gen_Boys", "Boys"),
        ("gen_Girls", "Girls"),
        ("gen_Unisex", "Unisex"),
    ]:
        if row.get(key) == "1":
            return label
    return None


def season_from_one_hot(row: dict[str, str]) -> str | None:
    for key, label in [
        ("sea_Spring", "Spring"),
        ("sea_Summer", "Summer"),
        ("sea_Fall", "Fall"),
        ("sea_Winter", "Winter"),
    ]:
        if row.get(key) == "1":
            return label
    return None


def usage_from_one_hot(row: dict[str, str]) -> str | None:
    for key, label in [
        ("usa_Casual", "Casual"),
        ("usa_Ethnic", "Ethnic"),
        ("usa_Formal", "Formal"),
        ("usa_Smart Casual", "Smart Casual"),
        ("usa_Sports", "Sports"),
    ]:
        if row.get(key) == "1":
            return label
    return None


def seed_products(limit: int | None = None) -> int:
    db = SessionLocal()
    inserted = 0

    try:
        with DEFAULT_CSV.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for index, row in enumerate(reader):
                if limit is not None and index >= limit:
                    break

                product_id = UUID(row["id"])
                exists = db.query(Product.id).filter(Product.id == product_id).first()
                if exists:
                    continue

                db.add(build_product(row))
                inserted += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return inserted


if __name__ == "__main__":
    raise SystemExit(
        "seed_products.py nạp dataset Myntra cũ và không còn khớp bảng products (đã đổi sang cột H&M).\n"
        "Sản phẩm giờ được nạp từ pipeline H&M: đăng nhập Data Scientist → Lịch chạy → Train AI."
    )
    inserted_count = seed_products()
    print(f"Inserted {inserted_count} products")
