"""Sinh backend/scripts.sql (PostgreSQL) từ các model SQLAlchemy.

    cd backend
    python scripts/dump_schema.py

Backend tự tạo bảng bằng Base.metadata.create_all khi khởi động; scripts.sql chỉ để tham khảo
hoặc dựng DB Postgres bằng tay. Chạy lại script này mỗi khi sửa models/.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")  # chỉ để import được config, không kết nối

from sqlalchemy import Enum  # noqa: E402
from sqlalchemy.dialects import postgresql  # noqa: E402
from sqlalchemy.schema import CreateIndex, CreateTable  # noqa: E402

from database import Base  # noqa: E402
import models  # noqa: E402,F401
from models import feedback_model, hm_model, interaction_model, model_ai_model, recommendation_model, sales_model  # noqa: E402,F401

HEADER = """-- Schema PostgreSQL sinh tự động từ backend/models — KHÔNG sửa tay.
-- Sinh lại:  cd backend && python scripts/dump_schema.py
-- Backend tự tạo bảng (Base.metadata.create_all) khi khởi động; file này để tham khảo / dựng DB bằng tay.
"""


def main():
    dialect = postgresql.dialect()
    lines = [HEADER]

    enums = {}
    for table in Base.metadata.sorted_tables:
        for column in table.columns:
            if isinstance(column.type, Enum):
                enums[column.type.name] = column.type.enums
    for name, values in enums.items():
        lines.append(f"CREATE TYPE {name} AS ENUM ({', '.join(repr(v) for v in values)});")
    lines.append("")

    for table in Base.metadata.sorted_tables:
        lines.append(str(CreateTable(table).compile(dialect=dialect)).strip() + ";")
        for index in sorted(table.indexes, key=lambda i: i.name):
            lines.append(str(CreateIndex(index).compile(dialect=dialect)).strip() + ";")
        lines.append("")

    out = BACKEND / "scripts.sql"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Đã ghi {out} ({len(Base.metadata.tables)} bảng)")


if __name__ == "__main__":
    main()
