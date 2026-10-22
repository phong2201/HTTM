"""Fixture chung: DB SQLite tạm + thư mục runs tạm → test không đụng DB thật.

Chạy:  cd backend && python -m pytest
"""
import os
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

_TMP = Path(tempfile.mkdtemp(prefix="hub_test_"))
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP / 'test.db'}"
os.environ["HM_RUNS_DIR"] = str(_TMP / "runs")

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402  (tạo bảng + admin mặc định quangkhaiadmin/123456)
from core.security import get_password_hash  # noqa: E402
from database import SessionLocal  # noqa: E402
from models.product_model import Product  # noqa: E402
from models.user_model import Role, User  # noqa: E402

PASSWORD = "123456"


@pytest.fixture(scope="session")
def client():
    # Không dùng `with TestClient(...)` → không bật thread hẹn giờ (pipeline 02:00, tổng hợp doanh số)
    return TestClient(main.app)


def _user(username: str, role: Role) -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(username=username).first():
            db.add(User(username=username, email=f"{username}@test.local",
                        password_hash=get_password_hash(PASSWORD), role_id=role))
            db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def tokens(client):
    _user("t_buyer", Role.BUYER)
    _user("t_ds", Role.DATA_SCIENTIST)
    login = lambda u: client.post("/auth/login", data={"username": u, "password": PASSWORD}).json()["access_token"]  # noqa: E731
    return {
        "buyer": {"Authorization": f"Bearer {login('t_buyer')}"},
        "ds": {"Authorization": f"Bearer {login('t_ds')}"},
        "admin": {"Authorization": f"Bearer {login('quangkhaiadmin')}"},
    }


@pytest.fixture(scope="session")
def products():
    """Vài sản phẩm theo cột articles.csv của H&M (2 màu cùng product_code + 1 món khác loại + 1 món đã ẩn)."""
    rows = [
        ("0108775015", "0108775", "Strap top", "Vest top", "Garment Upper body", "Ladieswear", 160000, True),
        ("0108775044", "0108775", "Strap top", "Vest top", "Garment Upper body", "Ladieswear", 160000, True),
        ("0110065001", "0110065", "OP T-shirt", "Bra", "Underwear", "Ladieswear", 450000, True),
        ("0111565001", "0111565", "20 den 1p Stockings", "Underwear Tights", "Socks & Tights", "Ladieswear", 107000, False),
    ]
    db = SessionLocal()
    try:
        out = {}
        for aid, code, name, ptype, group, index, price, active in rows:
            p = db.query(Product).filter_by(article_id=aid).first() or Product(
                id=uuid.uuid4(), article_id=aid, product_code=code, prod_name=name, product_type_name=ptype,
                product_group_name=group, index_group_name=index, price=price, is_active=active,
                quantity_in_stock=100, sales_last_week=10)
            db.add(p)
            db.commit()
            out[aid] = str(p.id)
        return out
    finally:
        db.close()
