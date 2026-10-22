"""Điều phối pipeline H&M + Random Forest (data_scientist/hm_pipeline/hub_pipeline.py).

Một lần chạy (run):
  1. Kaggle: đẩy script lên bằng `kaggle kernels push`, chờ xong, tải output về runs/<run_id>/.
     Local : chạy script bằng chính Python của backend, đọc progress.json để cập nhật tiến trình.
  2. Nạp kết quả (bước 6 · Ghi bảng Recommendations): catalog → products, liên kết Buyer ↔ customer_id,
     gợi ý → user_recommendations với một ModelVersion mới.
     Metrics kém baseline → chờ Data Scientist chọn "Vẫn ghi đè" / "Giữ bản cũ".

Trạng thái lưu ở runs/state.json, lịch sử ở runs/runs.json. Hẹn giờ chạy bằng một thread nền.
"""
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import HTTPException, status

from core.config import settings
from database import SessionLocal
from models.hm_model import UserCustomerLink
from models.model_ai_model import ModelVersion
from models.product_model import Product
from models.recommendation_model import UserRecommendation
from models.user_model import Role, User

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT_ROOT / "data_scientist" / "hm_pipeline" / "hub_pipeline.py"
RUNS_DIR = Path(settings.HM_RUNS_DIR) if settings.HM_RUNS_DIR else PROJECT_ROOT / "data_scientist" / "runs"
DATA_DIR = Path(settings.HM_DATA_DIR) if settings.HM_DATA_DIR else PROJECT_ROOT / "data" / "hm"
PRODUCT_IMAGES_DIR = PROJECT_ROOT / "data_scientist" / "images" / "hm"   # phục vụ qua /images/hm/
STATE_FILE = RUNS_DIR / "state.json"
HISTORY_FILE = RUNS_DIR / "runs.json"

TOTAL_STEPS = 6
KAGGLE_COMPETITION = "h-and-m-personalized-fashion-recommendations"
ARTICLE_NAMESPACE = uuid.UUID("6f1c5a4e-2b7d-4c1a-9a51-0d6a8e3f2b10")

# Khóa khớp với TrainingConfig ở front-end/src/services/api.ts
DEFAULT_CONFIG = {
    "schedule_enabled": True,
    "schedule_time": "02:00",
    "runner": "kaggle",          # "kaggle" | "local"
    "subset": "sample",          # "sample" | "full"
    "customer_frac": 0.1,
    "top_n": 12,
    "weeks": 4,
    "train_weeks": 3,
    "candidates_per_customer": 30,
    "neg_pos_ratio": 5,
    "n_estimators": 200,
    "max_depth": 12,
    "min_samples_leaf": 5,
}
PIPELINE_KEYS = ["runner", "subset", "customer_frac", "weeks", "train_weeks", "candidates_per_customer", "neg_pos_ratio",
                 "n_estimators", "max_depth", "min_samples_leaf", "top_n"]


def to_vnd(normalized_price: float) -> float:
    """Giá chuẩn hóa của H&M → VND ước lượng, làm tròn nghìn đồng."""
    return float(round(normalized_price * settings.HM_PRICE_TO_VND, -3))


def to_normalized(vnd: float) -> float:
    """Ngược lại của to_vnd — pipeline làm việc trên thang giá gốc của H&M."""
    return vnd / settings.HM_PRICE_TO_VND


def product_id_for(article_id: str) -> uuid.UUID:
    """UUID cố định cho mỗi article_id → nạp lại không tạo trùng sản phẩm."""
    return uuid.uuid5(ARTICLE_NAMESPACE, article_id)


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


class PipelineService:
    def __init__(self):
        self._lock = threading.RLock()
        self._worker: threading.Thread | None = None
        self._scheduler_started = False
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        state = _read_json(STATE_FILE, {})
        self.state = {
            "config": {**DEFAULT_CONFIG, **state.get("config", {})},
            "current": state.get("current"),
            "active_run_id": state.get("active_run_id"),
            "pending_run_id": state.get("pending_run_id"),
            "last_scheduled_date": state.get("last_scheduled_date"),
        }
        # Backend khởi động lại giữa chừng: kernel Kaggle vẫn chạy tiếp → theo dõi lại;
        # tiến trình local đã mất cùng backend → coi như lỗi.
        current = self.state["current"]
        if current and current.get("state") == "running":
            if current.get("runner") == "kaggle" and current.get("pushed"):
                self._worker = threading.Thread(target=self._resume_kaggle, args=(current["run_id"],), daemon=True)
                self._worker.start()
            else:
                current.update(state="failed", error="Backend khởi động lại khi đang chạy")
        self._save()

    # ------------------------------------------------------------ trạng thái

    def _save(self):
        _write_json(STATE_FILE, self.state)

    def _update_current(self, **changes):
        with self._lock:
            self.state["current"] = {**(self.state["current"] or {}), **changes}
            self._save()

    def is_running(self) -> bool:
        return bool(self._worker and self._worker.is_alive())

    def get_config(self) -> dict:
        return dict(self.state["config"])

    def save_config(self, config: dict) -> dict:
        with self._lock:
            merged = {**self.state["config"], **{k: v for k, v in config.items() if k in DEFAULT_CONFIG}}
            if merged["runner"] not in ("kaggle", "local") or merged["subset"] not in ("sample", "full"):
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "runner/subset không hợp lệ")
            self.state["config"] = merged
            self._save()
            return dict(merged)

    def next_run(self) -> datetime | None:
        cfg = self.state["config"]
        if not cfg["schedule_enabled"]:
            return None
        h, m = (int(x) for x in cfg["schedule_time"].split(":"))
        now = datetime.now()
        run = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if run <= now or self.state["last_scheduled_date"] == now.date().isoformat():
            run += timedelta(days=1)
        return run

    def status(self) -> dict:
        current = self.state["current"] or {}
        pending = self.state["pending_run_id"]
        pending_summary = self._summary(pending) if pending else None
        return {
            "run_id": current.get("run_id"),
            "runner": current.get("runner"),
            "state": current.get("state", "idle"),
            "completed_steps": current.get("completed_steps", 0),
            "current_step": current.get("current_step"),
            "started_at": current.get("started_at"),
            "finished_at": current.get("finished_at"),
            "error": current.get("error"),
            "next_run": self.next_run(),
            "active_run_id": self.state["active_run_id"],
            "config": self.get_config(),
            "exceptions": {
                "worse_than_baseline": bool(pending_summary and pending_summary.get("status") == "worse_than_baseline"),
                "data_error": current.get("error") if current.get("state") == "failed" else None,
            },
        }

    # ------------------------------------------------------------ chạy

    def trigger(self, source: str = "manual") -> dict:
        with self._lock:
            if self.is_running():
                raise HTTPException(status.HTTP_409_CONFLICT, "Pipeline đang chạy")
            cfg = self.get_config()
            run_id = datetime.now().strftime("run_%Y%m%d_%H%M%S")
            self.state["current"] = {
                "run_id": run_id, "runner": cfg["runner"], "source": source, "state": "running",
                "completed_steps": 0, "current_step": "Đang khởi động", "error": None,
                "started_at": datetime.now().isoformat(), "finished_at": None,
            }
            self._save()
            self._worker = threading.Thread(target=self._run, args=(run_id, cfg), daemon=True, name=f"hm-{run_id}")
            self._worker.start()
        where = "Kaggle" if cfg["runner"] == "kaggle" else "máy local"
        return {"message": f"Đã kích hoạt {run_id} trên {where}", "run_id": run_id}

    def _run(self, run_id: str, cfg: dict):
        run_dir = RUNS_DIR / run_id
        try:
            pipeline_cfg = {k: cfg[k] for k in PIPELINE_KEYS} | {"run_id": run_id}
            if cfg["runner"] == "kaggle":
                self._run_kaggle(run_dir, pipeline_cfg)
            else:
                self._run_local(run_dir, pipeline_cfg)
            self.import_run(run_id)
        except Exception as exc:  # noqa: BLE001 — mọi lỗi đều hiển thị ở màn Lịch chạy
            self._update_current(state="failed", error=str(exc), finished_at=datetime.now().isoformat())

    def _sync_progress(self, run_dir: Path):
        progress = _read_json(run_dir / "progress.json", None)
        if progress:
            self._update_current(completed_steps=progress["completed_steps"], current_step=progress.get("current_step"))
            if progress.get("state") == "failed":
                raise RuntimeError(f"Lỗi dữ liệu: {progress.get('error')}")

    # --- hành vi trên web → pipeline

    def export_app_events(self, path: Path) -> int:
        """Xuất đơn mua trên web (tài khoản đã liên kết customer_id, sản phẩm H&M) ra app_events.csv.

        Chỉ lấy đơn trong cửa sổ `weeks` tuần mà model dùng để tạo feature — đơn cũ hơn không ảnh hưởng gợi ý,
        nên dung lượng gửi đi không phình theo thời gian. Cột age_days giữ khoảng cách thời gian thật của đơn.
        Xem / giỏ / wishlist không xuất: chúng là ý định ngắn hạn, đã dùng trực tiếp lúc gọi /predict
        (services/session_rerank.py). Đơn gốc vẫn nằm nguyên trong DB.
        """
        from models.order_model import Order, OrderItem, OrderStatus

        window_days = int(self.state["config"]["weeks"]) * 7
        now = datetime.utcnow()
        since = now - timedelta(days=window_days)
        db = SessionLocal()
        try:
            rows = (db.query(UserCustomerLink.customer_id, Product.article_id, Order.order_date,
                             OrderItem.quantity, OrderItem.unit_price)
                      .join(Order, Order.id == OrderItem.order_id)
                      .join(UserCustomerLink, UserCustomerLink.user_id == Order.user_id)
                      .join(Product, Product.id == OrderItem.product_id)
                      .filter(Order.status != OrderStatus.CANCELLED, Product.article_id.isnot(None),
                              Order.order_date >= since)
                      .order_by(Order.order_date)
                      .all())
            linked = db.query(UserCustomerLink.customer_id).all()
        finally:
            db.close()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["customer_id", "article_id", "event", "ts", "age_days", "quantity", "price"])
            for customer_id, article_id, ts, quantity, price in rows:
                ts_naive = ts.replace(tzinfo=None) if ts and ts.tzinfo else ts
                age = min(window_days - 1, max(0, (now - ts_naive).days)) if ts_naive else 0
                writer.writerow([customer_id, article_id, "purchase", ts.isoformat() if ts else "", age, quantity,
                                 round(to_normalized(price), 6)])
            # Khách đã liên kết với tài khoản Buyer → pipeline luôn xuất gợi ý cho họ
            for (customer_id,) in linked:
                writer.writerow([customer_id, "", "link", "", "", 0, 0])
        return len(rows) + len(linked)

    def _sync_app_events_dataset(self, username: str) -> str | None:
        """Đẩy app_events.csv thành dataset riêng tư <username>/hub-app-events (mỗi lần chạy 1 version)."""
        slug = f"{username}/hub-app-events"
        folder = RUNS_DIR / "_app_events"
        shutil.rmtree(folder, ignore_errors=True)
        n = self.export_app_events(folder / "app_events.csv")
        try:
            self._kaggle("datasets", "status", slug, timeout=120)
            exists = True
        except RuntimeError:
            exists = False
        if not exists and n == 0:
            return None  # chưa có đơn nào trên web → không cần tạo dataset
        # Nội dung giống lần trước (bỏ cột age_days vì thay đổi theo ngày) → dùng lại version cũ, khỏi tải lên
        signature = self._events_signature(folder / "app_events.csv")
        if exists and signature == self.state.get("app_events_signature"):
            self._update_current(current_step="Không có đơn mới — dùng lại dataset hub-app-events")
            return slug
        _write_json(folder / "dataset-metadata.json", {
            "title": "hub-app-events", "id": slug, "licenses": [{"name": "CC0-1.0"}],
        })
        self._update_current(current_step=f"Đẩy {n} dòng mua trên web lên Kaggle")
        if exists:
            self._kaggle("datasets", "version", "-p", str(folder), "-m", self.state["current"]["run_id"])
        else:
            self._kaggle("datasets", "create", "-p", str(folder))
        deadline = time.time() + 600
        while time.time() < deadline:   # Kaggle cần xử lý xong version mới trước khi kernel đọc được
            if "ready" in self._kaggle("datasets", "status", slug, timeout=120).lower():
                with self._lock:
                    self.state["app_events_signature"] = signature
                    self._save()
                return slug
            time.sleep(15)
        raise RuntimeError("Dataset hub-app-events trên Kaggle xử lý quá 10 phút")

    @staticmethod
    def _events_signature(path: Path) -> str:
        import hashlib
        with open(path, encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f)]
        payload = "\n".join(f"{r['customer_id']},{r['article_id']},{r['event']},{r['ts']},{r['quantity']}" for r in rows)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _run_local(self, run_dir: Path, cfg: dict):
        if not (DATA_DIR / "transactions_train.csv").exists():
            raise RuntimeError(f"Lỗi dữ liệu: không thấy transactions_train.csv trong {DATA_DIR}")
        run_dir.mkdir(parents=True, exist_ok=True)
        cfg_file = run_dir / "config.json"
        _write_json(cfg_file, cfg)
        app_events = run_dir / "app_events.csv"
        self.export_app_events(app_events)
        with open(run_dir / "pipeline.log", "w", encoding="utf-8") as log:
            proc = subprocess.Popen(
                [sys.executable, str(SCRIPT), "--data-dir", str(DATA_DIR), "--out", str(run_dir), "--config", str(cfg_file),
                 "--app-events", str(app_events)],
                stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            while proc.poll() is None:
                time.sleep(2)
                self._sync_progress(run_dir)
        self._sync_progress(run_dir)
        if proc.returncode != 0:
            raise RuntimeError(f"Pipeline lỗi (mã {proc.returncode}) — xem {run_dir / 'pipeline.log'}")

    # --- Kaggle

    @staticmethod
    def _kaggle_exe() -> str:
        exe = shutil.which("kaggle") or str(Path(sys.executable).parent / "Scripts" / "kaggle.exe")
        if not Path(exe).exists() and not shutil.which(exe):
            raise RuntimeError("Không tìm thấy Kaggle CLI — cài bằng `pip install kaggle`")
        return exe

    @staticmethod
    def kernel_slug() -> str:
        if settings.KAGGLE_KERNEL_SLUG:
            return settings.KAGGLE_KERNEL_SLUG
        username = os.environ.get("KAGGLE_USERNAME")
        if not username:
            creds = _read_json(Path.home() / ".kaggle" / "kaggle.json", {})
            username = creds.get("username")
        if not username:
            raise RuntimeError("Chưa có kaggle.json — tạo token ở Kaggle → Settings → API và chép vào ~/.kaggle/")
        return f"{username}/hub-rf-pipeline"

    def _kaggle(self, *args: str, timeout: int = 600) -> str:
        # PYTHONUTF8: Kaggle CLI trên Windows mặc định đọc file bằng cp1252 → lỗi với script có tiếng Việt
        result = subprocess.run([self._kaggle_exe(), *args], capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout,
                                env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        if result.returncode != 0:
            raise RuntimeError(f"kaggle {' '.join(args[:2])}: {(result.stderr or result.stdout).strip()}")
        return result.stdout

    def _run_kaggle(self, run_dir: Path, cfg: dict):
        slug = self.kernel_slug()
        events_slug = self._sync_app_events_dataset(slug.split("/", 1)[0])
        kernel_dir = RUNS_DIR / "_kernel"
        shutil.rmtree(kernel_dir, ignore_errors=True)
        kernel_dir.mkdir(parents=True)
        source = SCRIPT.read_text(encoding="utf-8")
        injected = f"CONFIG_OVERRIDE = json.loads(r'''{json.dumps(cfg)}''')"
        # Thay cả dòng (kể cả chú thích phía sau) để không để lại text thừa
        source, n = re.subn(r"^CONFIG_OVERRIDE = None.*$", lambda _: injected, source, count=1, flags=re.M)
        if n != 1:
            raise RuntimeError("Script pipeline thiếu dòng CONFIG_OVERRIDE")
        (kernel_dir / SCRIPT.name).write_text(source, encoding="utf-8")
        _write_json(kernel_dir / "kernel-metadata.json", {
            "id": slug,
            "title": slug.split("/", 1)[1],
            "code_file": SCRIPT.name,
            "language": "python",
            "kernel_type": "script",
            "is_private": True,
            "enable_gpu": False,
            "enable_internet": False,
            "competition_sources": [KAGGLE_COMPETITION],
            "dataset_sources": [events_slug] if events_slug else [],
            "kernel_sources": [],
        })

        # Kaggle đôi khi lỗi hạ tầng trước khi script chạy (vd ERRORED_MOUNTING_DATASET) → đẩy lại.
        attempts = 3
        for attempt in range(1, attempts + 1):
            suffix = f" (lần {attempt}/{attempts})" if attempt > 1 else ""
            self._update_current(current_step=f"Đẩy notebook lên Kaggle{suffix}")
            self._kaggle("kernels", "push", "-p", str(kernel_dir))
            self._update_current(current_step=f"Đang chạy trên Kaggle{suffix}", pushed=True)
            time.sleep(20)
            try:
                self._wait_kaggle(slug, run_dir)
                return
            except RuntimeError:
                script_started = (run_dir / "progress.json").exists()
                if script_started or attempt == attempts:
                    raise
                time.sleep(120)

    def _resume_kaggle(self, run_id: str):
        try:
            self._wait_kaggle(self.kernel_slug(), RUNS_DIR / run_id)
            self.import_run(run_id)
        except Exception as exc:  # noqa: BLE001
            self._update_current(state="failed", error=str(exc), finished_at=datetime.now().isoformat())

    def _wait_kaggle(self, slug: str, run_dir: Path):
        deadline = time.time() + 12 * 3600
        while time.time() < deadline:
            out = self._kaggle("kernels", "status", slug).lower()
            if "complete" in out:
                break
            if "error" in out or "cancel" in out:
                self._download_kaggle_output(slug, run_dir)
                self._sync_progress(run_dir)
                raise RuntimeError(f"Kernel Kaggle lỗi: {out.strip()}")
            time.sleep(30)
        else:
            raise RuntimeError("Kernel Kaggle chạy quá 12 giờ")

        self._update_current(current_step="Tải kết quả từ Kaggle")
        self._download_kaggle_output(slug, run_dir)
        self._sync_progress(run_dir)

    def _download_kaggle_output(self, slug: str, run_dir: Path):
        run_dir.mkdir(parents=True, exist_ok=True)
        self._kaggle("kernels", "output", slug, "-p", str(run_dir), timeout=1800)

    # ------------------------------------------------------------ nạp kết quả (bước 6)

    def _summary(self, run_id: str | None) -> dict | None:
        return _read_json(RUNS_DIR / run_id / "summary.json", None) if run_id else None

    def import_run(self, run_id: str, force: bool = False) -> dict:
        """Nạp thư mục runs/<run_id> (từ Kaggle, local, hoặc tải tay từ Kaggle rồi giải nén vào đây)."""
        run_dir = RUNS_DIR / run_id
        summary = self._summary(run_id)
        missing = [f for f in ("summary.json", "recommendations.csv", "catalog.csv") if not (run_dir / f).exists()]
        if missing or not summary:
            raise RuntimeError(f"Lỗi dữ liệu: run {run_id} thiếu {', '.join(missing) or 'summary.json'}")

        self._record_history(summary)
        if summary.get("status") == "worse_than_baseline" and not force:
            with self._lock:
                self.state["pending_run_id"] = run_id
                self._save()
            self._update_current(state="done", completed_steps=5, current_step="Chờ quyết định ghi đè",
                                 finished_at=datetime.now().isoformat())
            return {"message": f"{run_id} kém hơn baseline — chưa ghi Recommendations", "written": False}

        self._update_current(completed_steps=5, current_step="Ghi bảng Recommendations")
        counts = self._write_to_db(run_id, run_dir)
        with self._lock:
            self.state["active_run_id"] = run_id
            self.state["pending_run_id"] = None
            self._save()
        self._set_history_status(run_id, "written")
        self._update_current(state="done", completed_steps=TOTAL_STEPS, current_step=None,
                             finished_at=datetime.now().isoformat())
        return {"message": f"Đã ghi {counts['recommendations']} gợi ý cho {counts['users']} tài khoản", "written": True, **counts}

    def _write_to_db(self, run_id: str, run_dir: Path) -> dict:
        db = SessionLocal()
        try:
            n_products = self._import_catalog(db, run_dir)

            for version in db.query(ModelVersion).filter(ModelVersion.is_active.is_(True)):
                version.is_active = False
            version = db.query(ModelVersion).filter(ModelVersion.version_tag == run_id).first()
            if not version:
                version = ModelVersion(version_tag=run_id)
                db.add(version)
            version.is_active = True
            version.model_weights_path = str(run_dir.relative_to(PROJECT_ROOT)) if run_dir.is_relative_to(PROJECT_ROOT) else str(run_dir)
            version.product_count = n_products
            db.flush()

            recs = self._read_recommendations(run_dir)
            links = self._link_buyers(db, list(recs))
            n_recs = self._write_recommendations(db, version.id, recs, links, int(self.state["config"]["top_n"]))
            db.commit()
            return {"products": n_products, "users": len(links), "recommendations": n_recs}
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _import_catalog(self, db, run_dir: Path) -> int:
        PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        images_src = run_dir / "images"
        if (run_dir / "images.zip").exists() and not images_src.exists():
            shutil.unpack_archive(run_dir / "images.zip", images_src)
        existing = {p.id: p for p in db.query(Product).filter(Product.article_id.isnot(None))}
        count = 0
        with open(run_dir / "catalog.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                aid = row["article_id"]
                src = images_src / f"{aid}.jpg"
                if src.exists():
                    shutil.copyfile(src, PRODUCT_IMAGES_DIR / f"{aid}.jpg")
                has_image = (PRODUCT_IMAGES_DIR / f"{aid}.jpg").exists()
                pid = product_id_for(aid)
                product = existing.get(pid) or Product(id=pid, article_id=aid, quantity_in_stock=100)
                product.product_code = f"{int(row['product_code']):07d}" if row.get("product_code") else aid[:7]
                product.prod_name = row["prod_name"] or aid
                product.product_type_name = row["product_type_name"] or None
                product.product_group_name = row["product_group_name"] or None
                product.colour_group_name = row["colour_group_name"] or None
                product.graphical_appearance_name = row["graphical_appearance_name"] or None
                product.index_group_name = row["index_group_name"] or None
                product.detail_desc = row["detail_desc"] or None
                product.price = to_vnd(float(row["price"] or 0))
                product.sales_last_week = int(float(row.get("sales_1w") or 0))
                product.image_url = f"{settings.PUBLIC_BASE_URL}/images/hm/{aid}.jpg" if has_image else None
                product.is_active = True
                db.add(product)
                count += 1
        db.flush()
        return count

    @staticmethod
    def _read_recommendations(run_dir: Path) -> dict[str, list[tuple[str, int, float]]]:
        recs: dict[str, list[tuple[str, int, float]]] = {}
        with open(run_dir / "recommendations.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                recs.setdefault(row["customer_id"], []).append((row["article_id"], int(row["rank"]), float(row["score"])))
        for items in recs.values():
            items.sort(key=lambda x: x[1])
        return recs

    @staticmethod
    def _link_buyers(db, customers: list[str]) -> dict:
        """Gán mỗi Buyer một customer_id có gợi ý trong run này.

        Pipeline luôn tạo gợi ý cho khách đã liên kết (gửi kèm trong app_events.csv), nên liên kết cũ được giữ.
        Nếu run không có gợi ý cho khách đó (vd nạp run cũ) → gán lại khách khác để tài khoản không bị trống.
        """
        have_recs = set(customers)
        rows = {link.user_id: link for link in db.query(UserCustomerLink)}
        taken = {link.customer_id for link in rows.values()}
        available = [c for c in customers if c not in taken]
        buyers = db.query(User).filter(User.role_id == Role.BUYER).order_by(User.created_at).all()
        for buyer in buyers:
            link = rows.get(buyer.id)
            if link and link.customer_id in have_recs:
                continue
            if not available:
                break
            customer_id = available.pop(0)
            if link:
                link.customer_id = customer_id
            else:
                link = UserCustomerLink(user_id=buyer.id, customer_id=customer_id)
                db.add(link)
                rows[buyer.id] = link
        db.flush()
        links = {uid: link.customer_id for uid, link in rows.items()}
        return {uid: cid for uid, cid in links.items() if cid in set(customers)}

    @staticmethod
    def _write_recommendations(db, version_id, recs: dict, links: dict, top_n: int) -> int:
        db.query(UserRecommendation).filter(UserRecommendation.version_id == version_id).delete(synchronize_session=False)
        rows = []
        for user_id, customer_id in links.items():
            for article_id, rank, score in recs.get(customer_id, [])[:top_n]:
                rows.append(UserRecommendation(user_id=user_id, product_id=product_id_for(article_id),
                                               score=score, rank=rank, version_id=version_id))
        db.bulk_save_objects(rows)
        return len(rows)

    def recompute(self, top_n: int) -> dict:
        """Khối "Adjust n": ghi lại Recommendations của run đang dùng với Top n mới (≤ export_top_k)."""
        run_id = self.state["active_run_id"]
        if not run_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chưa có run nào được ghi vào Recommendations")
        self.save_config({"top_n": top_n})
        db = SessionLocal()
        try:
            version = db.query(ModelVersion).filter(ModelVersion.version_tag == run_id).first()
            recs = self._read_recommendations(RUNS_DIR / run_id)
            links = {l.user_id: l.customer_id for l in db.query(UserCustomerLink) if l.customer_id in recs}
            n = self._write_recommendations(db, version.id, recs, links, top_n)
            db.commit()
        finally:
            db.close()
        return {"message": f"Đã tính lại Top {top_n}: {n} gợi ý cho {len(links)} tài khoản"}

    def resolve(self, action: str) -> dict:
        pending = self.state["pending_run_id"]
        current = self.state["current"] or {}
        if action == "overwrite":
            if not pending:
                raise HTTPException(status.HTTP_409_CONFLICT, "Không có run nào đang chờ ghi đè")
            return self.import_run(pending, force=True)
        with self._lock:
            self.state["pending_run_id"] = None
            if current.get("state") == "failed":
                current["error"] = None
                current["state"] = "idle"
            self._save()
        return {"message": "Giữ bản Recommendations hiện tại"}

    # ------------------------------------------------------------ lịch sử & số liệu

    def _record_history(self, summary: dict):
        with self._lock:
            history = [r for r in _read_json(HISTORY_FILE, []) if r["run_id"] != summary["run_id"]]
            cfg = summary.get("config", {})
            history.append({
                "run_id": summary["run_id"],
                "created_at": summary.get("created_at"),
                "subset": f"{summary.get('subset')} · {summary.get('runner')}",
                "n_estimators": cfg.get("n_estimators"),
                "max_depth": cfg.get("max_depth"),
                "val_map12": summary.get("metrics", {}).get("map12"),
                "status": summary.get("status"),
            })
            _write_json(HISTORY_FILE, history)

    def _set_history_status(self, run_id: str, value: str):
        with self._lock:
            history = _read_json(HISTORY_FILE, [])
            for r in history:
                if r["run_id"] == run_id:
                    r["status"] = value
            _write_json(HISTORY_FILE, history)

    def _display_run_id(self) -> str | None:
        """Run hiển thị ở màn metrics: run đang chờ quyết định, hoặc run đang dùng, hoặc run mới nhất."""
        history = _read_json(HISTORY_FILE, [])
        return self.state["pending_run_id"] or self.state["active_run_id"] or (history[-1]["run_id"] if history else None)

    def metrics(self) -> dict:
        run_id = self._display_run_id()
        summary = self._summary(run_id)
        if not summary:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chưa có lần chạy nào — bấm Train AI")
        runs = sorted(_read_json(HISTORY_FILE, []), key=lambda r: r.get("created_at") or "", reverse=True)
        return {
            "run_id": summary["run_id"],
            "created_at": summary.get("created_at"),
            "metrics": summary.get("metrics", {}),
            "baselines": summary.get("baselines"),
            "split": summary.get("split"),
            "runs": runs,
        }

    def error_analysis(self) -> dict:
        data = _read_json(RUNS_DIR / (self._display_run_id() or "_none") / "error_analysis.json", None)
        if not data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chưa có kết quả phân tích lỗi")
        return data

    def insights(self) -> dict:
        """Hai thẻ nhận xét ở màn Data Science — mọi con số lấy từ kết quả run, không viết tay."""
        run_id = self._display_run_id()
        summary = self._summary(run_id)
        if not summary:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chưa có lần chạy nào")
        run_dir = RUNS_DIR / run_id
        return {
            "run_id": run_id,
            "trend": self._trend_items(run_dir),
            "optimization": self._optimization_items(summary, _read_json(run_dir / "error_analysis.json", {})),
        }

    @staticmethod
    def _trend_items(run_dir: Path) -> list[str]:
        data = _read_json(run_dir / "insights.json", None)
        pct = lambda x: f"{x:.0%}"  # noqa: E731
        if data:
            items = [f"Tuần cuối dữ liệu ({data['week']}): {data['transactions']:,} lượt mua "
                     f"({data['transactions'] / max(data['transactions_prev'], 1) - 1:+.0%} so với tuần trước).".replace(",", ".")]
            if data["top_groups"]:
                items.append("Nhóm bán chạy nhất: " + ", ".join(f"{g['name']} ({pct(g['share'])})" for g in data["top_groups"]) + ".")
            if data["rising"]:
                items.append("Tăng mạnh nhất so với tuần trước: " + ", ".join(f"{g['name']} ({g['pct']:+.0%})" for g in data["rising"]) + ".")
            if data["falling"]:
                items.append("Giảm: " + ", ".join(f"{g['name']} ({g['pct']:+.0%})" for g in data["falling"]) + ".")
            items.append("Theo danh mục: " + ", ".join(f"{g['name']} {pct(g['share'])}" for g in data["index_share"]) + ".")
            items.append(f"Giá trung vị ~{to_vnd(data['median_price']):,.0f}₫ (quy đổi ước lượng); "
                         f"{pct(data['online_share'])} lượt mua qua kênh online.".replace(",", "."))
            return items

        # Run cũ chưa có insights.json → tính từ lượt bán tuần của catalog
        groups, types, total = {}, {}, 0
        path = run_dir / "catalog.csv"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    n = int(float(row.get("sales_1w") or 0))
                    total += n
                    groups[row["product_group_name"]] = groups.get(row["product_group_name"], 0) + n
                    types[row["product_type_name"]] = types.get(row["product_type_name"], 0) + n
        if not total:
            return []
        top = lambda d, k: sorted(d.items(), key=lambda x: -x[1])[:k]  # noqa: E731
        return [
            f"Trong {total:,} lượt mua tuần cuối của các sản phẩm đang bán trên HUB:".replace(",", "."),
            "Nhóm bán chạy nhất: " + ", ".join(f"{g} ({n / total:.0%})" for g, n in top(groups, 3)) + ".",
            "Loại sản phẩm nổi bật: " + ", ".join(t for t, _ in top(types, 5)) + ".",
            "Chạy lại pipeline để có so sánh với tuần trước.",
        ]

    @staticmethod
    def _optimization_items(summary: dict, analysis: dict) -> list[str]:
        m, bl = summary.get("metrics", {}), summary.get("baselines", {}) or {}
        best_name, best = max(((k, v.get("map12") or 0) for k, v in bl.items()), key=lambda x: x[1], default=("", 0))
        names = {"bestseller": "top bán chạy", "repurchase": "mua lại gần nhất"}
        items = []
        if m.get("map12") is not None and best:
            items.append(f"Random Forest MAP@12 = {m['map12']:.4f}, {m['map12'] / best - 1:+.0%} so với baseline "
                         f"mạnh nhất ({names.get(best_name, best_name)}: {best:.4f}).")
        cr = m.get("candidate_recall")
        sources = [s for s in analysis.get("candidate_recall", []) if s["source"] != "Tất cả nguồn" and s.get("recall") is not None]
        if cr is not None:
            line = f"Recall ứng viên {cr:.1%}: {1 - cr:.0%} món khách thật sự mua không lọt vào danh sách ứng viên — đây là giới hạn trên của model."
            if sources:
                top = max(sources, key=lambda s: s["recall"])
                line += f" Nguồn đóng góp nhiều nhất: {top['source']} ({top['recall']:.1%})."
            items.append(line)
        segs = analysis.get("by_customer", [])
        cold = next((s for s in segs if s["segment"] == "cold start"), None)
        warm = [s for s in segs if s["segment"] != "cold start" and s.get("map12") is not None]
        total = sum(s.get("customers") or 0 for s in segs)
        if cold and warm and total:
            warm_map = sum(s["map12"] * s["customers"] for s in warm) / max(sum(s["customers"] for s in warm), 1)
            items.append(f"Khách cold start chiếm {cold['customers'] / total:.0%} với MAP@12 {cold['map12'] or 0:.4f}, "
                         f"so với {warm_map:.4f} của khách có lịch sử → cần nguồn ứng viên/feature riêng cho nhóm này.")
        groups = [g for g in analysis.get("by_product_group", []) if (g.get("purchases") or 0) >= 1000]
        if groups:
            weak = min(groups, key=lambda g: g.get("recall12") or 0)
            items.append(f"Nhóm sản phẩm gợi ý kém nhất (trong nhóm mua nhiều): {weak['product_group_name']} "
                         f"(Recall@12 {weak['recall12']:.3f}).")
        feats = [f["feature"] for f in analysis.get("feature_importance", [])[:3]]
        if feats:
            items.append("Feature quan trọng nhất: " + ", ".join(feats) + ".")
        return items

    def eda_reports(self) -> dict:
        run_id = self._display_run_id()
        result = {"run_id": run_id, "original": [], "normalized": []}
        if not run_id:
            return result
        for group in ("original", "normalized"):
            folder = RUNS_DIR / run_id / "reports" / group
            for png in sorted(folder.glob("*.png")) if folder.exists() else []:
                result[group].append({"file": png.name, "url": f"{settings.PUBLIC_BASE_URL}/ai/reports/{run_id}/{group}/{png.name}"})
        return result

    @staticmethod
    def report_path(run_id: str, group: str, name: str) -> Path:
        path = (RUNS_DIR / run_id / "reports" / group / name).resolve()
        if group not in ("original", "normalized") or not path.is_relative_to(RUNS_DIR.resolve()) or not path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Không có báo cáo")
        return path

    def bestseller_ids(self, limit: int) -> list[uuid.UUID]:
        ids = _read_json(RUNS_DIR / (self.state["active_run_id"] or "_none") / "bestsellers.json", [])
        return [product_id_for(a) for a in ids[:limit]]

    # ------------------------------------------------------------ hẹn giờ

    def start_scheduler(self):
        if self._scheduler_started:
            return
        self._scheduler_started = True
        threading.Thread(target=self._scheduler_loop, daemon=True, name="hm-scheduler").start()

    def _scheduler_loop(self):
        while True:
            try:
                cfg = self.state["config"]
                now = datetime.now()
                h, m = (int(x) for x in cfg["schedule_time"].split(":"))
                due = now.replace(hour=h, minute=m, second=0, microsecond=0)
                today = now.date().isoformat()
                # Chỉ chạy trong 1 giờ sau giờ hẹn → mở máy buổi trưa không tự kích hoạt.
                if (cfg["schedule_enabled"] and due <= now < due + timedelta(hours=1)
                        and self.state["last_scheduled_date"] != today and not self.is_running()):
                    with self._lock:
                        self.state["last_scheduled_date"] = today
                        self._save()
                    self.trigger(source="schedule")
            except Exception as exc:  # noqa: BLE001
                print(f"[hm-scheduler] {exc}", flush=True)
            time.sleep(30)


pipeline = PipelineService()
