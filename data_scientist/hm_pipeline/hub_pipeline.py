"""HUB · Pipeline gợi ý H&M với Random Forest làm ranker.

Chạy được ở hai nơi, cùng một file:
  - Kaggle (script kernel, dataset gắn sẵn): backend đẩy file này lên bằng `kaggle kernels push`,
    cấu hình được chèn vào dòng CONFIG_OVERRIDE bên dưới.
  - Máy local:  python hub_pipeline.py --data-dir D:/HTTM/data/hm --out D:/HTTM/data_scientist/runs/run_x

Các bước (progress.json cập nhật sau mỗi bước):
  1. Chọn subset & chia theo thời gian   (train week / val week / test week)
  2. Sinh ứng viên                         (mua lại, bán chạy tuần, cùng product_code, co-purchase)
  3. Tạo feature
  4. Huấn luyện Random Forest
  5. Đánh giá vs baseline                  (BL1 top-12 bán chạy, BL2 mua lại gần nhất)
  6. Ghi bảng Recommendations              — do backend làm khi nạp thư mục kết quả.

Mọi feature chỉ tính từ giao dịch trước cutoff của tuần nhãn (chống rò rỉ).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import sys

import numpy as np
import pandas as pd

# Console Windows mặc định cp1252 → lỗi khi in tiếng Việt
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONFIG_OVERRIDE = None  # <HUB_CONFIG> — backend thay dòng này khi đẩy lên Kaggle

DEFAULT_CONFIG = {
    "run_id": None,
    "runner": "local",
    "subset": "sample",          # "sample" | "full"
    "customer_frac": 0.10,       # chỉ dùng khi subset = "sample"
    "weeks": 4,                  # số tuần lịch sử để tạo feature
    "train_weeks": 3,            # số tuần nhãn dùng để train (các tuần ngay trước tuần val)
    "candidates_per_customer": 30,
    "neg_pos_ratio": 5,
    "n_estimators": 200,
    "max_depth": 12,
    "min_samples_leaf": 5,
    "top_n": 12,
    "export_top_k": 50,          # số gợi ý/khách xuất ra để backend "Điều chỉnh Top n"
    "demo_customers": 300,       # số khách xuất gợi ý để liên kết với tài khoản Buyer
    "catalog_size": 2000,        # số sản phẩm xuất ra làm catalog cho web
    "image_size": 256,
    "seed": 42,
}

STEPS = [
    "Chọn subset & chia theo thời gian",
    "Sinh ứng viên",
    "Tạo feature",
    "Huấn luyện Random Forest",
    "Đánh giá vs baseline",
    "Ghi bảng Recommendations",
]

SOURCES = {
    "src_repurchase": "Mua lại",
    "src_bestseller": "Bán chạy tuần",
    "src_samecode": "Cùng product_code",
    "src_copurchase": "Co-purchase",
    "src_agebest": "Bán chạy theo tuổi",
}
SOURCE_PRIORITY = {"src_repurchase": 16, "src_copurchase": 8, "src_samecode": 4, "src_agebest": 2, "src_bestseller": 1}
AGE_BINS = [0, 25, 35, 45, 55, 200]   # nhóm tuổi cho nguồn "Bán chạy theo tuổi"

SEGMENTS = ["cold start", "1–2 giao dịch", "3–10 giao dịch", ">10 giao dịch"]

ARTICLE_STATIC = [
    "product_type_no", "graphical_appearance_no", "colour_group_code", "perceived_colour_value_id",
    "department_no", "index_group_no", "section_no", "garment_group_no",
]

FEATURES = [
    # khách
    "c_n_tx", "c_n_articles", "c_days_since_last", "c_avg_price", "c_online_ratio", "c_age",
    # sản phẩm
    "a_cnt_window", "a_cnt_1w", "a_n_customers", "a_avg_price", "a_days_since_first", "pg_code",
    *ARTICLE_STATIC,
    # cặp khách × sản phẩm
    "ca_cnt", "ca_days_since", "c_group_share", "c_code_cnt", "price_diff", "bestseller_rank", "agebest_rank",
    *SOURCES.keys(),
]

DAY = pd.Timedelta(days=1)


# ---------------------------------------------------------------- tiện ích

class Progress:
    def __init__(self, out: Path):
        self.path = out / "progress.json"
        self.started = time.time()
        self.write(0, "running")

    def write(self, completed: int, state: str, error: str | None = None):
        payload = {
            "completed_steps": completed,
            "state": state,
            "current_step": STEPS[completed] if completed < len(STEPS) else None,
            "elapsed_sec": round(time.time() - self.started, 1),
            "error": error,
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[progress] {completed}/{len(STEPS)} · {state}" + (f" · {error}" if error else ""), flush=True)


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def customer_to_int(ids: pd.Series) -> np.ndarray:
    """customer_id H&M (64 ký tự hex) → int64 từ 16 ký tự cuối (không trùng trên dataset này)."""
    return ids.str[-16:].map(lambda x: int(x, 16)).to_numpy(dtype=np.uint64).view(np.int64)


def find_app_events(explicit: str | None) -> Path | None:
    """app_events.csv do backend xuất (đơn hàng trên web HUB). Kaggle: gắn qua dataset <user>/hub-app-events."""
    if explicit:
        return Path(explicit) if Path(explicit).exists() else None
    hits = glob.glob("/kaggle/input/**/app_events.csv", recursive=True)
    return Path(hits[0]) if hits else None


def load_app_purchases(path: Path | None, end: pd.Timestamp) -> pd.DataFrame | None:
    """Đơn mua trên web → dòng giao dịch H&M, dời về cuối dữ liệu: ngày = end - 1 - age_days.

    Dataset H&M dừng ở 2020-09-22 còn web chạy ở hiện tại → giữ khoảng cách thời gian thật (đơn hôm qua
    gần cutoff hơn đơn 6 tuần trước), backend chỉ gửi đơn trong cửa sổ feature nên age_days < weeks*7.
    Chỉ dùng cho bước tạo gợi ý cuối (không đưa vào train/val/test → không làm sai số đánh giá).
    """
    if path is None:
        return None
    ev = pd.read_csv(path, dtype={"customer_id": str, "article_id": str})
    ev = ev[(ev["event"] == "purchase") & ev["article_id"].notna()]
    if ev.empty:
        return None
    ev = ev.loc[ev.index.repeat(ev["quantity"].clip(lower=1).astype(int))]
    age = pd.to_numeric(ev.get("age_days", 0), errors="coerce").fillna(0).clip(lower=0).astype(int)
    return pd.DataFrame({
        "t_dat": (end - DAY - pd.to_timedelta(age, unit="D")).to_numpy(),
        "article_id": ev["article_id"].astype(np.int32).to_numpy(),
        "price": ev["price"].astype(np.float32).to_numpy(),
        "sales_channel_id": np.int8(2),
        "customer": customer_to_int(ev["customer_id"]),
        "online": np.int8(1),
    })


def load_linked_customers(path: Path | None) -> np.ndarray:
    """customer_id đã liên kết với tài khoản Buyer trên web (dòng event = link)."""
    if path is None:
        return np.array([], dtype=np.int64)
    ev = pd.read_csv(path, dtype={"customer_id": str, "article_id": str})
    ids = ev.loc[ev["event"] == "link", "customer_id"].dropna()
    return customer_to_int(ids) if len(ids) else np.array([], dtype=np.int64)


def find_data_dir(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    hits = glob.glob("/kaggle/input/**/articles.csv", recursive=True)
    if not hits:
        raise FileNotFoundError("Không tìm thấy articles.csv — truyền --data-dir hoặc gắn dataset H&M vào kernel")
    return Path(hits[0]).parent


def split_label(start: pd.Timestamp) -> str:
    return f"{start:%Y-%m-%d} → {start + 6 * DAY:%Y-%m-%d}"


# ---------------------------------------------------------------- 1 · nạp & chia dữ liệu

def load_data(data_dir: Path, cfg: dict, reports: Path):
    tx_path = data_dir / "transactions_train.csv"

    log("Đọc cột t_dat để tìm mốc thời gian")
    days = pd.read_csv(tx_path, usecols=["t_dat"], dtype={"t_dat": "category"})["t_dat"]
    daily = days.value_counts().sort_index()
    daily.index = pd.to_datetime(daily.index.astype(str))
    del days
    end = daily.index.max() + DAY                        # mốc loại trừ
    test_start, val_start = end - 7 * DAY, end - 14 * DAY
    n_train = max(1, int(cfg.get("train_weeks", 1)))
    train_starts = [val_start - 7 * i * DAY for i in range(n_train, 0, -1)]   # cũ → mới
    train_start = train_starts[0]
    window_start = train_start - cfg["weeks"] * 7 * DAY
    min_str = f"{window_start:%Y-%m-%d}"

    log(f"Đọc giao dịch từ {min_str} (chunk)")
    parts, price_sample = [], []
    for chunk in pd.read_csv(
        tx_path, chunksize=2_000_000,
        dtype={"t_dat": str, "customer_id": str, "article_id": np.int32, "price": np.float32, "sales_channel_id": np.int8},
    ):
        price_sample.append(chunk["price"].sample(frac=0.01, random_state=cfg["seed"]))
        parts.append(chunk[chunk["t_dat"] >= min_str])
    tx = pd.concat(parts, ignore_index=True)
    del parts
    tx["t_dat"] = pd.to_datetime(tx["t_dat"])
    tx["customer"] = customer_to_int(tx["customer_id"])
    tx = tx.drop(columns="customer_id")
    tx["online"] = (tx["sales_channel_id"] == 2).astype(np.int8)
    log(f"Cửa sổ dữ liệu: {len(tx):,} giao dịch, {tx.customer.nunique():,} khách")

    articles = pd.read_csv(data_dir / "articles.csv", dtype={"article_id": np.int32})
    articles["pg_code"] = articles["product_group_name"].astype("category").cat.codes.astype(np.int16)

    customers = pd.read_csv(data_dir / "customers.csv", usecols=["customer_id", "age"])
    customers["customer"] = customer_to_int(customers["customer_id"])

    eda_original(daily, pd.concat(price_sample), articles, customers, tx, reports / "original")
    split = {"train": train_start, "train_weeks": train_starts, "val": val_start, "test": test_start, "end": end}
    return tx, articles, customers, split


def sample_customers(customer_ints: np.ndarray, cfg: dict) -> np.ndarray:
    if cfg["subset"] == "full":
        return np.ones(len(customer_ints), dtype=bool)
    # Lấy mẫu theo hash → cố định giữa các lần chạy
    bucket = (customer_ints.astype(np.uint64) % np.uint64(10_000)).astype(np.int64)
    return bucket < int(cfg["customer_frac"] * 10_000)


# ---------------------------------------------------------------- 2 · ứng viên

def source_sizes(cfg: dict) -> dict:
    """Số món lấy từ mỗi nguồn — tăng theo candidates_per_customer để ngưỡng cấu hình có tác dụng."""
    cap = int(cfg["candidates_per_customer"])
    return {
        "repurchase": max(12, cap // 4),
        "bestseller": max(12, cap // 4),
        "agebest": max(12, cap // 4),
        "samecode": max(3, cap // 20),    # mỗi product_code khách từng mua
        "copurchase": max(3, cap // 10),  # mỗi món khách từng mua
    }


def copurchase_pairs(hist: pd.DataFrame, top: int = 3) -> pd.DataFrame:
    last = hist["t_dat"].max()
    b = hist.loc[hist["t_dat"] > last - 14 * DAY, ["customer", "t_dat", "article_id"]].drop_duplicates()
    size = b.groupby(["customer", "t_dat"])["article_id"].transform("size")
    b = b[(size > 1) & (size <= 10)]
    p = b.merge(b, on=["customer", "t_dat"])
    p = p[p["article_id_x"] != p["article_id_y"]]
    cnt = p.groupby(["article_id_x", "article_id_y"]).size().rename("n").reset_index()
    cnt = cnt.sort_values("n", ascending=False).groupby("article_id_x").head(top)
    return cnt.rename(columns={"article_id_x": "article_id", "article_id_y": "co_article"})[["article_id", "co_article"]]


def bestsellers(hist: pd.DataFrame, k: int = 12) -> np.ndarray:
    last = hist["t_dat"].max()
    return hist.loc[hist["t_dat"] > last - 7 * DAY, "article_id"].value_counts().head(k).index.to_numpy()


def age_buckets(customers: pd.DataFrame) -> pd.Series:
    """customer → nhóm tuổi (0..4), -1 = không rõ tuổi."""
    bucket = pd.cut(customers["age"], AGE_BINS, labels=False, right=False)
    return pd.Series(bucket.fillna(-1).astype(np.int8).to_numpy(), index=customers["customer"].to_numpy())


def age_bestsellers(hist: pd.DataFrame, bucket_of: pd.Series, k: int) -> pd.DataFrame:
    """Top k bán chạy tuần gần nhất trong từng nhóm tuổi → [bucket, article_id, agebest_rank]."""
    last = hist["t_dat"].max()
    lw = hist.loc[hist["t_dat"] > last - 7 * DAY, ["customer", "article_id"]]
    lw = lw.assign(bucket=lw["customer"].map(bucket_of).fillna(-1).astype(np.int8))
    top = (lw.groupby(["bucket", "article_id"]).size().rename("n").reset_index()
             .sort_values(["bucket", "n"], ascending=[True, False]).groupby("bucket").head(k))
    top["agebest_rank"] = top.groupby("bucket").cumcount() + 1
    return top[["bucket", "article_id", "agebest_rank"]]


def gen_candidates(hist: pd.DataFrame, customers: np.ndarray, articles: pd.DataFrame, cust_df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    sizes = source_sizes(cfg)
    code_of = articles.set_index("article_id")["product_code"]
    h = hist[hist["customer"].isin(customers)]

    rep = (h.sort_values("t_dat", ascending=False)
            .drop_duplicates(["customer", "article_id"])
            .groupby("customer").head(sizes["repurchase"])[["customer", "article_id"]])

    best = bestsellers(hist, sizes["bestseller"])
    best_df = pd.DataFrame({
        "customer": np.repeat(customers, len(best)),
        "article_id": np.tile(best, len(customers)),
    })

    # Bán chạy theo nhóm tuổi — chủ yếu giúp khách cold start (không có lịch sử mua)
    bucket_of = age_buckets(cust_df)
    cust_bucket = pd.DataFrame({
        "customer": customers,
        "bucket": pd.Series(customers).map(bucket_of).fillna(-1).astype(np.int8).to_numpy(),
    })
    age_df = cust_bucket.merge(age_bestsellers(hist, bucket_of, sizes["agebest"]), on="bucket")[["customer", "article_id"]]

    pop = hist["article_id"].value_counts()
    art_pop = pd.DataFrame({"article_id": pop.index, "pop": pop.values})
    art_pop["product_code"] = art_pop["article_id"].map(code_of)
    top_by_code = art_pop.sort_values("pop", ascending=False).groupby("product_code").head(sizes["samecode"])
    same = (rep.assign(product_code=rep["article_id"].map(code_of))[["customer", "product_code"]]
            .drop_duplicates()
            .merge(top_by_code[["product_code", "article_id"]], on="product_code")[["customer", "article_id"]])

    co = (rep.merge(copurchase_pairs(hist, sizes["copurchase"]), on="article_id")[["customer", "co_article"]]
            .rename(columns={"co_article": "article_id"}))

    parts = []
    for src, df in [("src_repurchase", rep), ("src_bestseller", best_df), ("src_samecode", same),
                    ("src_copurchase", co), ("src_agebest", age_df)]:
        df = df[["customer", "article_id"]].copy()
        for s in SOURCES:
            df[s] = np.int8(1 if s == src else 0)
        parts.append(df)
    cand = pd.concat(parts, ignore_index=True).groupby(["customer", "article_id"], as_index=False)[list(SOURCES)].max()

    # Giới hạn số ứng viên/khách theo độ ưu tiên nguồn rồi độ phổ biến
    cand["priority"] = sum(cand[s].astype(np.int16) * w for s, w in SOURCE_PRIORITY.items())
    cand["pop"] = cand["article_id"].map(pop).fillna(0).astype(np.float32)
    cap = max(int(cfg["candidates_per_customer"]), len(best))
    cand = (cand.sort_values(["customer", "priority", "pop"], ascending=[True, False, False])
                .groupby("customer").head(cap)
                .drop(columns=["priority", "pop"])
                .reset_index(drop=True))
    return cand


# ---------------------------------------------------------------- 3 · feature

def build_features(cand: pd.DataFrame, hist: pd.DataFrame, articles: pd.DataFrame, customers: pd.DataFrame, cutoff: pd.Timestamp, cfg: dict) -> pd.DataFrame:
    art = articles.set_index("article_id")
    h = hist[hist["customer"].isin(cand["customer"].unique())].copy()
    h["pg_code"] = h["article_id"].map(art["pg_code"]).astype(np.int16)
    h["product_code"] = h["article_id"].map(art["product_code"])

    c = h.groupby("customer").agg(
        c_n_tx=("article_id", "size"), c_n_articles=("article_id", "nunique"),
        c_last=("t_dat", "max"), c_avg_price=("price", "mean"), c_online_ratio=("online", "mean"),
    )
    c["c_days_since_last"] = (cutoff - c.pop("c_last")).dt.days

    last_week = hist["t_dat"] > hist["t_dat"].max() - 7 * DAY
    a = hist.groupby("article_id").agg(
        a_cnt_window=("customer", "size"), a_n_customers=("customer", "nunique"),
        a_avg_price=("price", "mean"), a_first=("t_dat", "min"),
    )
    a["a_cnt_1w"] = hist[last_week].groupby("article_id").size()
    a["a_days_since_first"] = (cutoff - a.pop("a_first")).dt.days

    ca = h.groupby(["customer", "article_id"]).agg(ca_cnt=("t_dat", "size"), ca_last=("t_dat", "max"))
    ca["ca_days_since"] = (cutoff - ca.pop("ca_last")).dt.days
    cg = (h.groupby(["customer", "pg_code"]).size() / h.groupby("customer").size()).rename("c_group_share")
    cc = h.groupby(["customer", "product_code"]).size().rename("c_code_cnt")

    best = bestsellers(hist, source_sizes(cfg)["bestseller"])
    best_rank = pd.Series(np.arange(1, len(best) + 1), index=best, name="bestseller_rank")

    df = cand.merge(c, left_on="customer", right_index=True, how="left")
    df = df.merge(a, left_on="article_id", right_index=True, how="left")
    df = df.merge(art[["pg_code", "product_code", *ARTICLE_STATIC]], left_on="article_id", right_index=True, how="left")
    df = df.merge(ca, left_on=["customer", "article_id"], right_index=True, how="left")
    df = df.merge(cg, left_on=["customer", "pg_code"], right_index=True, how="left")
    df = df.merge(cc, left_on=["customer", "product_code"], right_index=True, how="left")
    df["bestseller_rank"] = df["article_id"].map(best_rank).fillna(99)
    bucket_of = age_buckets(customers)
    df["bucket"] = df["customer"].map(bucket_of).fillna(-1).astype(np.int8)
    df = df.merge(age_bestsellers(hist, bucket_of, source_sizes(cfg)["agebest"]), on=["bucket", "article_id"], how="left")
    df["agebest_rank"] = df["agebest_rank"].fillna(99)
    df["c_age"] = df["customer"].map(customers.set_index("customer")["age"])
    df["price_diff"] = df["a_avg_price"] - df["c_avg_price"]

    fill = {"ca_cnt": 0, "c_group_share": 0, "c_code_cnt": 0, "a_cnt_1w": 0, "c_n_tx": 0, "c_n_articles": 0}
    df = df.fillna(fill)
    df[FEATURES] = df[FEATURES].astype(np.float32).fillna(-1)
    return df


def labels_for(tx: pd.DataFrame, start: pd.Timestamp) -> pd.DataFrame:
    week = tx[(tx["t_dat"] >= start) & (tx["t_dat"] < start + 7 * DAY)]
    return week[["customer", "article_id"]].drop_duplicates()


def history_for(tx: pd.DataFrame, cutoff: pd.Timestamp, weeks: int) -> pd.DataFrame:
    return tx[(tx["t_dat"] < cutoff) & (tx["t_dat"] >= cutoff - weeks * 7 * DAY)]


def week_dataset(tx, articles, customers, start, sampled, cfg):
    """Ứng viên + feature + nhãn cho tuần bắt đầu `start` (chỉ khách có mua trong tuần, đã lấy mẫu)."""
    labels = labels_for(tx, start)
    labels = labels[sampled(labels["customer"].to_numpy())]
    target_customers = labels["customer"].unique()
    hist = history_for(tx, start, cfg["weeks"])
    cand = gen_candidates(hist, target_customers, articles, customers, cfg)
    feats = build_features(cand, hist, articles, customers, start, cfg)
    feats["label"] = feats.set_index(["customer", "article_id"]).index.isin(
        labels.set_index(["customer", "article_id"]).index).astype(np.int8)
    return feats, labels, hist


# ---------------------------------------------------------------- 5 · đánh giá

def apk(actual: set, predicted: list, k: int = 12) -> float:
    hits, score = 0, 0.0
    for i, p in enumerate(predicted[:k]):
        if p in actual:
            hits += 1
            score += hits / (i + 1)
    return score / min(len(actual), k) if actual else 0.0


def ndcg(actual: set, predicted: list, k: int = 12) -> float:
    dcg = sum(1 / np.log2(i + 2) for i, p in enumerate(predicted[:k]) if p in actual)
    idcg = sum(1 / np.log2(i + 2) for i in range(min(len(actual), k)))
    return dcg / idcg if idcg else 0.0


def evaluate(preds: dict, actual: dict, k: int = 12) -> dict:
    rows = []
    for cust, items in actual.items():
        p = preds.get(cust, [])
        hits = len(set(p[:k]) & items)
        rows.append((apk(items, p, k), hits / len(items), hits / k, ndcg(items, p, k)))
    m = np.array(rows) if rows else np.zeros((1, 4))
    return {"map12": float(m[:, 0].mean()), "recall12": float(m[:, 1].mean()),
            "precision12": float(m[:, 2].mean()), "ndcg12": float(m[:, 3].mean())}


def top_k(scored: pd.DataFrame, k: int) -> dict:
    top = scored.sort_values(["customer", "score"], ascending=[True, False]).groupby("customer").head(k)
    return top.groupby("customer")["article_id"].agg(list).to_dict()


def baseline_preds(hist: pd.DataFrame, customers, k: int = 12) -> tuple[dict, dict]:
    best = list(bestsellers(hist, k))
    bl1 = {c: best for c in customers}
    recent = (hist[hist["customer"].isin(customers)].sort_values("t_dat", ascending=False)
              .drop_duplicates(["customer", "article_id"]).groupby("customer")["article_id"].agg(list))
    bl2 = {}
    for c in customers:
        items = list(recent.get(c, []))[:k]
        items += [a for a in best if a not in items][: k - len(items)]
        bl2[c] = items
    return bl1, bl2


def error_analysis(val, val_actual, val_preds, val_hist, articles, model, k: int = 12) -> dict:
    n_tx = val_hist.groupby("customer").size()

    def segment(c):
        n = n_tx.get(c, 0)
        return SEGMENTS[0] if n == 0 else SEGMENTS[1] if n <= 2 else SEGMENTS[2] if n <= 10 else SEGMENTS[3]

    seg_rows = {s: [] for s in SEGMENTS}
    for c, items in val_actual.items():
        p = val_preds.get(c, [])
        seg_rows[segment(c)].append((apk(items, p, k), len(set(p[:k]) & items) / len(items)))
    by_customer = [{
        "segment": s,
        "customers": len(r),
        "map12": float(np.mean([x[0] for x in r])) if r else None,
        "recall12": float(np.mean([x[1] for x in r])) if r else None,
    } for s, r in seg_rows.items()]

    group_of = articles.set_index("article_id")["product_group_name"]
    actual_pairs = pd.DataFrame([(c, a) for c, s in val_actual.items() for a in s], columns=["customer", "article_id"])
    rec_pairs = pd.DataFrame([(c, a) for c, p in val_preds.items() for a in p[:k]], columns=["customer", "article_id"])
    actual_pairs["hit"] = actual_pairs.set_index(["customer", "article_id"]).index.isin(rec_pairs.set_index(["customer", "article_id"]).index)
    rec_pairs["hit"] = rec_pairs.set_index(["customer", "article_id"]).index.isin(actual_pairs.set_index(["customer", "article_id"]).index)
    actual_pairs["g"] = actual_pairs["article_id"].map(group_of)
    rec_pairs["g"] = rec_pairs["article_id"].map(group_of)
    ra = actual_pairs.groupby("g").agg(purchases=("hit", "size"), recall12=("hit", "mean"))
    rp = rec_pairs.groupby("g")["hit"].mean().rename("precision12")
    groups = ra.join(rp, how="left").sort_values("purchases", ascending=False)
    by_group = [{
        "product_group_name": str(g),
        "purchases": int(r.purchases),
        "precision12": None if pd.isna(r.precision12) else float(r.precision12),
        "recall12": float(r.recall12),
    } for g, r in groups.iterrows()]

    importance = sorted(zip(FEATURES, model.feature_importances_), key=lambda x: -x[1])[:8]

    cand_pairs = val.set_index(["customer", "article_id"])
    actual_idx = actual_pairs.set_index(["customer", "article_id"]).index
    recall_by_source = []
    for src, name in SOURCES.items():
        covered = cand_pairs.index[cand_pairs[src].to_numpy() == 1]
        recall_by_source.append({"source": name, "recall": float(actual_idx.isin(covered).mean())})
    recall_by_source.append({"source": "Tất cả nguồn", "recall": float(actual_idx.isin(cand_pairs.index).mean())})

    return {
        "by_customer": by_customer,
        "by_product_group": by_group,
        "feature_importance": [{"feature": f, "importance": float(v)} for f, v in importance],
        "candidate_recall": recall_by_source,
    }


# ---------------------------------------------------------------- EDA

def _save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    import matplotlib.pyplot as plt
    plt.close(fig)


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold"})
    return plt


def trend_insights(tx: pd.DataFrame, articles: pd.DataFrame) -> dict:
    """Xu hướng tuần cuối so với tuần trước (số liệu thật từ transactions) cho thẻ "Xu hướng sản phẩm"."""
    last = tx["t_dat"].max()
    cur = tx[tx["t_dat"] > last - 7 * DAY]
    prev = tx[(tx["t_dat"] <= last - 7 * DAY) & (tx["t_dat"] > last - 14 * DAY)]
    art = articles.set_index("article_id")

    def by(df, col):
        return df["article_id"].map(art[col]).value_counts()

    cur_g, prev_g = by(cur, "product_group_name"), by(prev, "product_group_name")
    growth = pd.DataFrame({"cur": cur_g, "prev": prev_g}).fillna(0)
    growth = growth[(growth["cur"] >= 500) & (growth["prev"] >= 500)]   # bỏ nhóm quá nhỏ
    growth["pct"] = growth["cur"] / growth["prev"] - 1
    growth = growth.sort_values("pct", ascending=False)

    cur_t = by(cur, "product_type_name")
    index_share = by(cur, "index_group_name") / len(cur)
    return {
        "week": f"{last - 6 * DAY:%Y-%m-%d} → {last:%Y-%m-%d}",
        "transactions": int(len(cur)),
        "transactions_prev": int(len(prev)),
        "top_groups": [{"name": str(k), "share": float(v / len(cur))} for k, v in cur_g.head(3).items()],
        "top_types": [{"name": str(k), "count": int(v)} for k, v in cur_t.head(5).items()],
        "rising": [{"name": str(k), "pct": float(r.pct)} for k, r in growth.head(3).iterrows() if r.pct > 0],
        "falling": [{"name": str(k), "pct": float(r.pct)} for k, r in growth.tail(3)[::-1].iterrows() if r.pct < 0],
        "index_share": [{"name": str(k), "share": float(v)} for k, v in index_share.items()],
        "median_price": float(cur["price"].median()),
        "online_share": float(cur["online"].mean()),
    }


def eda_original(daily, prices, articles, customers, tx, out: Path):
    plt = _plt()
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(daily.index, daily.values, color="#E8112D", lw=1)
    ax.set_title("Số giao dịch mỗi ngày (toàn bộ dữ liệu)")
    _save(fig, out / "3_1_1_transactions_per_day.png")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.hist(prices, bins=80, color="#FF7A3D")
    ax.set_title("Phân phối giá (đã chuẩn hóa, mẫu 1%)")
    _save(fig, out / "3_1_2_price_distribution.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    articles["product_group_name"].value_counts().head(15)[::-1].plot.barh(ax=ax, color="#FF5E7E")
    ax.set_title("Số sản phẩm theo product_group_name (top 15)")
    _save(fig, out / "3_1_3_product_group_counts.png")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.hist(customers["age"].dropna(), bins=60, color="#FFA62B")
    ax.set_title(f"Tuổi khách hàng (thiếu {customers['age'].isna().mean():.1%})")
    _save(fig, out / "3_1_4_customer_age.png")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    idx = tx["article_id"].map(articles.set_index("article_id")["index_group_name"])
    idx.value_counts().plot.bar(ax=ax, color="#FF7EB3", rot=0)
    ax.set_title("Lượt mua theo index_group_name (cửa sổ dữ liệu)")
    _save(fig, out / "3_1_5_index_group_sales.png")


def eda_normalized(tx, split, stats: dict, out: Path):
    plt = _plt()
    weekly = tx.set_index("t_dat").resample("W-TUE")["article_id"].size()
    fig, ax = plt.subplots(figsize=(9, 3.6))
    colors = ["#FFC9B3" if d < split["train"] else "#FF7A3D" if d < split["val"] else "#FFC93C" if d < split["test"] else "#E8112D" for d in weekly.index - 6 * DAY]
    ax.bar(weekly.index, weekly.values, width=5, color=colors)
    ax.set_title("Giao dịch theo tuần: lịch sử · train · val · test")
    _save(fig, out / "3_3_1_time_split.png")

    per_cust = tx.groupby("customer").size()
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.hist(np.log1p(per_cust), bins=50, color="#FF5E7E")
    ax.set_title("log(1 + số giao dịch/khách) trong cửa sổ")
    _save(fig, out / "3_3_2_purchases_per_customer.png")

    pop = tx["article_id"].value_counts().to_numpy()
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.loglog(np.arange(1, len(pop) + 1), pop, color="#E8112D")
    ax.set_title("Đuôi dài độ phổ biến sản phẩm (log-log)")
    _save(fig, out / "3_3_3_article_popularity_longtail.png")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    counts = {SOURCES[s]: stats["sources"][s] for s in SOURCES}
    ax.bar(counts.keys(), counts.values(), color=["#FF7A3D", "#FF5E7E", "#FFA62B", "#FF7EB3", "#E8112D"])
    ax.set_title("Số ứng viên theo nguồn (các tuần train)")
    _save(fig, out / "3_3_4_candidate_sources.png")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar(["Dương", "Âm (gốc)", "Âm (sau lấy mẫu)"], [stats["pos"], stats["neg"], stats["fit_neg"]], color=["#2E7D4F", "#DCCFD2", "#FF7A3D"])
    ax.set_title("Cân bằng nhãn trước/sau lấy mẫu âm")
    _save(fig, out / "3_3_5_label_balance.png")


# ---------------------------------------------------------------- xuất kết quả

def export_catalog(out: Path, data_dir: Path, articles, tx, rec_articles, cfg):
    last_week = tx["t_dat"] > tx["t_dat"].max() - 7 * DAY
    popular = tx.loc[last_week, "article_id"].value_counts().head(cfg["catalog_size"]).index
    ids = pd.Index(rec_articles).union(popular)
    price = tx.groupby("article_id")["price"].mean()
    sales_1w = tx[last_week].groupby("article_id").size()
    cols = ["article_id", "product_code", "prod_name", "product_type_name", "product_group_name",
            "colour_group_name", "graphical_appearance_name", "index_group_name", "detail_desc"]
    cat = articles.loc[articles["article_id"].isin(ids), cols].copy()
    cat["price"] = cat["article_id"].map(price).round(6)
    cat["sales_1w"] = cat["article_id"].map(sales_1w).fillna(0).astype(int)
    cat["article_id"] = cat["article_id"].map(lambda a: f"{a:010d}")
    cat.to_csv(out / "catalog.csv", index=False)

    images_dir = data_dir / "images"
    copied = 0
    if images_dir.exists():
        from PIL import Image
        dst = out / "images"
        dst.mkdir(exist_ok=True)
        for aid in cat["article_id"]:
            src = images_dir / aid[:3] / f"{aid}.jpg"
            if src.exists():
                with Image.open(src) as im:
                    im.thumbnail((cfg["image_size"], cfg["image_size"]))
                    im.convert("RGB").save(dst / f"{aid}.jpg", quality=85)
                copied += 1
        # Gom ảnh thành 1 file: Kaggle CLI chỉ tải trang đầu danh sách output (~500 file)
        import shutil
        shutil.make_archive(str(out / "images"), "zip", dst)
        shutil.rmtree(dst)
    log(f"Catalog {len(cat):,} sản phẩm, {copied:,} ảnh")
    return len(cat), copied


# ---------------------------------------------------------------- main

def run(cfg: dict, data_dir: Path, out: Path, app_events: Path | None = None):
    from sklearn.ensemble import RandomForestClassifier

    out.mkdir(parents=True, exist_ok=True)
    reports = out / "reports"
    progress = Progress(out)
    rng = np.random.default_rng(cfg["seed"])
    k = 12
    try:
        # 1
        tx, articles, customers, split = load_data(data_dir, cfg, reports)
        sampled = lambda ids: sample_customers(ids, cfg)
        progress.write(1, "running")

        # 2 + 3 (ứng viên và feature cho từng tuần). Mỗi tuần train lấy mẫu âm ngay để tiết kiệm RAM.
        stats = {"pos": 0, "neg": 0, "fit_neg": 0, "rows": 0, "sources": {s: 0 for s in SOURCES}}
        fit_parts = []
        for i, start in enumerate(split["train_weeks"], 1):
            log(f"Tuần train {i}/{len(split['train_weeks'])}: {split_label(start)}")
            week, _, _ = week_dataset(tx, articles, customers, start, sampled, cfg)
            pos = week[week["label"] == 1]
            neg = week[week["label"] == 0]
            n_neg = min(len(neg), int(len(pos) * cfg["neg_pos_ratio"]))
            fit_parts.append(pd.concat([pos, neg.sample(n=n_neg, random_state=cfg["seed"] + i)]))
            stats["pos"] += len(pos)
            stats["neg"] += len(neg)
            stats["fit_neg"] += n_neg
            stats["rows"] += len(week)
            for s in SOURCES:
                stats["sources"][s] += int(week[s].sum())
            del week, pos, neg
        fit = pd.concat(fit_parts, ignore_index=True)
        del fit_parts
        progress.write(2, "running")
        log("Tuần val / test")
        val, val_labels, val_hist = week_dataset(tx, articles, customers, split["val"], sampled, cfg)
        test, test_labels, test_hist = week_dataset(tx, articles, customers, split["test"], sampled, cfg)
        progress.write(3, "running")

        # 4
        log(f"Huấn luyện RF trên {len(fit):,} dòng ({stats['pos']:,} dương, {len(split['train_weeks'])} tuần nhãn)")
        model = RandomForestClassifier(
            n_estimators=int(cfg["n_estimators"]), max_depth=int(cfg["max_depth"]),
            min_samples_leaf=int(cfg["min_samples_leaf"]), n_jobs=-1, random_state=cfg["seed"],
        )
        model.fit(fit[FEATURES], fit["label"])
        eda_normalized(tx, split, stats, reports / "normalized")
        progress.write(4, "running")

        # 5
        def score_week(feats, labels, hist):
            feats = feats.assign(score=model.predict_proba(feats[FEATURES])[:, 1])
            actual = labels.groupby("customer")["article_id"].agg(set).to_dict()
            preds = top_k(feats, k)
            bl1, bl2 = baseline_preds(hist, list(actual), k)
            cand_idx = feats.set_index(["customer", "article_id"]).index
            lab_idx = labels.set_index(["customer", "article_id"]).index
            metrics = evaluate(preds, actual, k) | {"candidate_recall": float(lab_idx.isin(cand_idx).mean())}
            return feats, actual, preds, metrics, evaluate(bl1, actual, k), evaluate(bl2, actual, k)

        val, val_actual, val_preds, val_m, bl1_m, bl2_m = score_week(val, val_labels, val_hist)
        _, _, _, test_m, test_bl1, test_bl2 = score_week(test, test_labels, test_hist)
        log(f"VAL MAP@12 RF={val_m['map12']:.5f} · BL1={bl1_m['map12']:.5f} · BL2={bl2_m['map12']:.5f}")
        status = "written" if val_m["map12"] >= max(bl1_m["map12"], bl2_m["map12"]) else "worse_than_baseline"
        analysis = error_analysis(val, val_actual, val_preds, val_hist, articles, model, k)
        progress.write(5, "running")

        # Xuất gợi ý cho tuần kế tiếp (sau dữ liệu) cho các khách hoạt động nhiều nhất → liên kết tài khoản Buyer
        hist = history_for(tx, split["end"], cfg["weeks"])
        demo = hist["customer"].value_counts().head(cfg["demo_customers"]).index.to_numpy()
        linked = load_linked_customers(app_events)
        if len(linked):
            demo = np.union1d(demo, linked)
            log(f"Luôn tạo gợi ý cho {len(linked):,} khách đã liên kết tài khoản Buyer")
        app = load_app_purchases(app_events, split["end"])
        if app is not None:
            app = app[app["article_id"].isin(articles["article_id"])]   # bỏ món không có trong articles.csv
        n_app = 0 if app is None else len(app)
        if n_app:
            hist = pd.concat([hist, app], ignore_index=True)
            demo = np.union1d(demo, app["customer"].unique())
            log(f"Thêm {n_app:,} món mua trên web HUB của {app['customer'].nunique():,} khách vào lịch sử")
        prod = build_features(gen_candidates(hist, demo, articles, customers, cfg), hist, articles, customers, split["end"], cfg)
        prod["score"] = model.predict_proba(prod[FEATURES])[:, 1]
        prod = prod.sort_values(["customer", "score"], ascending=[True, False]).groupby("customer").head(cfg["export_top_k"])
        prod["rank"] = prod.groupby("customer").cumcount() + 1
        id_map = customers.set_index("customer")["customer_id"]
        recs = pd.DataFrame({
            "customer_id": prod["customer"].map(id_map).to_numpy(),
            "article_id": prod["article_id"].map(lambda a: f"{a:010d}").to_numpy(),
            "rank": prod["rank"].to_numpy(),
            "score": prod["score"].round(6).to_numpy(),
        })
        recs.to_csv(out / "recommendations.csv", index=False)
        best_next = [f"{a:010d}" for a in bestsellers(hist, 50)]
        (out / "bestsellers.json").write_text(json.dumps(best_next), encoding="utf-8")
        n_catalog, n_images = export_catalog(out, data_dir, articles, tx,
                                             set(prod["article_id"]) | {int(a) for a in best_next}, cfg)

        summary = {
            "run_id": cfg["run_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "runner": cfg["runner"],
            "subset": "full" if cfg["subset"] == "full" else f"sample {cfg['customer_frac']:.0%}",
            "config": cfg,
            "split": {
                "train": (f"{split['train']:%Y-%m-%d} → {split['val'] - DAY:%Y-%m-%d} "
                          f"({len(split['train_weeks'])} tuần nhãn) · feature từ {cfg['weeks']} tuần trước mỗi tuần"),
                "val": split_label(split["val"]),
                "test": split_label(split["test"]),
            },
            "metrics": val_m,
            "test_metrics": test_m,
            "baselines": {"bestseller": bl1_m, "repurchase": bl2_m},
            "test_baselines": {"bestseller": test_bl1, "repurchase": test_bl2},
            "status": status,
            "counts": {
                "window_transactions": int(len(tx)), "train_rows": int(stats["rows"]), "train_weeks": len(split["train_weeks"]), "fit_rows": int(len(fit)),
                "val_customers": len(val_actual), "demo_customers": int(len(demo)), "app_purchases": int(n_app),
                "recommendations": int(len(recs)), "catalog": n_catalog, "images": n_images,
            },
        }
        (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "error_analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "insights.json").write_text(json.dumps(trend_insights(tx, articles), ensure_ascii=False, indent=2), encoding="utf-8")
        progress.write(5, "done")
        log(f"Xong · {status}")
    except Exception as exc:  # ghi lỗi để backend báo "Lỗi dữ liệu"
        progress.write(0, "failed", f"{type(exc).__name__}: {exc}")
        raise


def main():
    parser = argparse.ArgumentParser(description="HUB · H&M Random Forest pipeline")
    parser.add_argument("--data-dir", help="Thư mục chứa articles.csv, customers.csv, transactions_train.csv")
    parser.add_argument("--out", default="/kaggle/working" if Path("/kaggle/working").exists() else "out")
    parser.add_argument("--config", help="File JSON ghi đè DEFAULT_CONFIG")
    parser.add_argument("--app-events", help="app_events.csv do backend xuất (mặc định: tìm trong /kaggle/input)")
    args = parser.parse_args()

    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_OVERRIDE:
        cfg.update(CONFIG_OVERRIDE)
    if args.config:
        cfg.update(json.loads(Path(args.config).read_text(encoding="utf-8")))
    cfg["run_id"] = cfg["run_id"] or datetime.now().strftime("run_%Y%m%d_%H%M%S")
    log(f"Cấu hình: {json.dumps(cfg, ensure_ascii=False)}")
    app_events = find_app_events(args.app_events)
    log(f"Hành vi web: {app_events or 'không có'}")
    run(cfg, find_data_dir(args.data_dir), Path(args.out), app_events)


if __name__ == "__main__":
    main()
