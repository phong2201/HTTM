"""Kiểm thử pipeline ML (data_scientist/hm_pipeline/hub_pipeline.py): metric, chia theo thời gian, chống rò rỉ.

Dữ liệu ở đây là bảng nhỏ dựng tay để kiểm tra logic — không phải dữ liệu của hệ thống.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data_scientist" / "hm_pipeline"))
import hub_pipeline as hp  # noqa: E402

D = pd.Timestamp


# ---------------------------------------------------------------- metric

def test_apk_dung_dinh_nghia_kaggle():
    # trúng ở vị trí 1 và 3, khách mua 2 món → (1/1 + 2/3) / 2
    assert hp.apk({1, 3}, [1, 2, 3]) == pytest.approx((1 + 2 / 3) / 2)
    assert hp.apk({9}, [1, 2, 3]) == 0
    assert hp.apk(set(), [1, 2]) == 0


def test_apk_chi_tinh_12_vi_tri_dau():
    assert hp.apk({13}, list(range(1, 14))) == 0


def test_ndcg_hoan_hao_bang_1():
    assert hp.ndcg({1, 2}, [1, 2, 3]) == pytest.approx(1.0)
    assert hp.ndcg({2}, [1, 2]) == pytest.approx(1 / np.log2(3))


def test_evaluate_trung_binh_theo_khach():
    m = hp.evaluate({"a": [1], "b": [5]}, {"a": {1}, "b": {6}})
    assert m["map12"] == pytest.approx(0.5)
    assert m["recall12"] == pytest.approx(0.5)
    assert m["precision12"] == pytest.approx(0.5 / 12)


# ---------------------------------------------------------------- chia dữ liệu & rò rỉ

@pytest.fixture
def tx():
    rows = [
        (D("2020-09-01"), 1, 100, 0.02), (D("2020-09-05"), 1, 101, 0.03),   # lịch sử của khách 1
        (D("2020-09-10"), 1, 102, 0.04),                                      # tuần nhãn
        (D("2020-09-12"), 2, 100, 0.02),                                      # tuần nhãn, khách 2 cold start
        (D("2020-09-20"), 1, 103, 0.05),                                      # SAU tuần nhãn (tương lai)
    ]
    df = pd.DataFrame(rows, columns=["t_dat", "customer", "article_id", "price"])
    df["sales_channel_id"] = np.int8(2)
    df["online"] = np.int8(1)
    df["article_id"] = df["article_id"].astype(np.int32)
    return df


def test_history_chi_lay_truoc_cutoff(tx):
    hist = hp.history_for(tx, D("2020-09-08"), weeks=4)
    assert hist["t_dat"].max() < D("2020-09-08")
    assert set(hist["article_id"]) == {100, 101}


def test_nhan_chi_lay_dung_tuan(tx):
    labels = hp.labels_for(tx, D("2020-09-08"))
    assert set(map(tuple, labels[["customer", "article_id"]].to_numpy())) == {(1, 102), (2, 100)}


@pytest.fixture
def articles():
    return pd.DataFrame({
        "article_id": np.array([100, 101, 102, 103], dtype=np.int32),
        "product_code": [100, 100, 102, 103],
        "product_group_name": ["A", "A", "B", "B"],
        **{c: [1, 1, 2, 2] for c in hp.ARTICLE_STATIC},
    }).assign(pg_code=lambda d: d["product_group_name"].astype("category").cat.codes.astype(np.int16))


@pytest.fixture
def customers():
    return pd.DataFrame({"customer": np.array([1, 2], dtype=np.int64), "age": [30.0, np.nan], "customer_id": ["c1", "c2"]})


def test_feature_khong_doi_khi_them_du_lieu_tuong_lai(tx, articles, customers):
    """Chống rò rỉ: thêm giao dịch sau cutoff không được làm đổi bất kỳ feature nào."""
    cfg = dict(hp.DEFAULT_CONFIG, candidates_per_customer=12)
    cutoff = D("2020-09-08")

    def feats(data):
        hist = hp.history_for(data, cutoff, cfg["weeks"])
        cand = hp.gen_candidates(hist, np.array([1, 2]), articles, customers, cfg)
        return hp.build_features(cand, hist, articles, customers, cutoff, cfg).sort_values(["customer", "article_id"]).reset_index(drop=True)

    base = feats(tx)
    future = pd.concat([tx, tx.assign(t_dat=D("2020-09-15"), article_id=np.int32(103))], ignore_index=True)
    pd.testing.assert_frame_equal(base[hp.FEATURES], feats(future)[hp.FEATURES])


def test_khach_cold_start_van_co_ung_vien(tx, articles, customers):
    cfg = dict(hp.DEFAULT_CONFIG, candidates_per_customer=12)
    hist = hp.history_for(tx, D("2020-09-08"), cfg["weeks"])
    cand = hp.gen_candidates(hist, np.array([2]), articles, customers, cfg)
    assert len(cand) > 0 and (cand["src_repurchase"] == 0).all()


def test_lay_mau_khach_co_dinh_giua_cac_lan_chay():
    ids = np.arange(1, 100_000, dtype=np.int64)
    cfg = dict(hp.DEFAULT_CONFIG, subset="sample", customer_frac=0.1)
    a, b = hp.sample_customers(ids, cfg), hp.sample_customers(ids, cfg)
    assert (a == b).all() and 0.08 < a.mean() < 0.12


def test_don_tren_web_giu_khoang_cach_thoi_gian(tmp_path):
    f = tmp_path / "app_events.csv"
    f.write_text("customer_id,article_id,event,ts,age_days,quantity,price\n"
                 f"{'0' * 48}{'1' * 16},0000000100,purchase,,0,1,0.02\n"
                 f"{'0' * 48}{'1' * 16},0000000101,purchase,,10,2,0.03\n"
                 f"{'0' * 48}{'1' * 16},,link,,,0,0\n", encoding="utf-8")
    end = D("2020-09-23")
    app = hp.load_app_purchases(f, end)
    assert len(app) == 3                                            # quantity 2 → 2 dòng
    assert set(app["t_dat"]) == {end - pd.Timedelta(days=1), end - pd.Timedelta(days=11)}
    assert len(hp.load_linked_customers(f)) == 1
