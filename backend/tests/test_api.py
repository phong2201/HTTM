"""Kiểm thử API: xác thực, phân quyền theo role, kiểm tra đầu vào, luồng mua hàng, gợi ý, doanh số."""


# ---------------------------------------------------------------- xác thực & phân quyền

def test_login_sai_mat_khau(client):
    r = client.post("/auth/login", data={"username": "kuroisme", "password": "sai"})
    assert r.status_code == 401


def test_dang_ky_thieu_truong_bi_tu_choi(client):
    assert client.post("/auth/register", json={"username": "x"}).status_code == 422


def test_dang_ky_trung_username(client, tokens):
    r = client.post("/auth/register", json={"username": "t_buyer", "email": "khac@test.local", "password": "123456"})
    assert r.status_code in (400, 409)


def test_khong_token_bi_chan(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/ai/training/status").status_code == 401


def test_buyer_khong_vao_duoc_admin_va_data_science(client, tokens):
    assert client.get("/dashboard/metrics", headers=tokens["buyer"]).status_code == 403
    assert client.get("/dashboard/sales", headers=tokens["buyer"]).status_code == 403
    assert client.get("/ai/training/status", headers=tokens["buyer"]).status_code == 403
    assert client.post("/ai/trigger-training", headers=tokens["buyer"]).status_code == 403


def test_data_scientist_vao_duoc_ai_nhung_khong_vao_admin(client, tokens):
    assert client.get("/ai/training/status", headers=tokens["ds"]).status_code == 200
    assert client.get("/dashboard/metrics", headers=tokens["ds"]).status_code == 403


# ---------------------------------------------------------------- sản phẩm & kiểm tra đầu vào

def test_danh_sach_chi_gom_san_pham_dang_ban(client, tokens, products):
    ids = {p["id"] for p in client.get("/products/?limit=100", headers=tokens["buyer"]).json()}
    assert products["0108775015"] in ids
    assert products["0111565001"] not in ids          # is_active = False


def test_id_san_pham_sai_dinh_dang(client, tokens):
    assert client.get("/products/khong-phai-uuid", headers=tokens["buyer"]).status_code == 422


def test_admin_tao_san_pham_thieu_gia(client, tokens):
    r = client.post("/products/", headers=tokens["admin"], json={"prod_name": "Thiếu giá"})
    assert r.status_code == 422


def test_buyer_khong_tao_duoc_san_pham(client, tokens):
    r = client.post("/products/", headers=tokens["buyer"], json={"prod_name": "x", "price": 1000})
    assert r.status_code == 403


def test_cau_hinh_pipeline_ngoai_mien_bi_tu_choi(client, tokens):
    assert client.put("/ai/training/config", headers=tokens["ds"], json={"top_n": 0}).status_code == 422
    assert client.put("/ai/training/config", headers=tokens["ds"], json={"runner": "colab"}).status_code == 422
    assert client.put("/ai/training/config", headers=tokens["ds"], json={"schedule_time": "25h"}).status_code == 422


# ---------------------------------------------------------------- đặt hàng

def test_don_hang_rong_bi_tu_choi(client, tokens):
    assert client.post("/orders", headers=tokens["buyer"], json={"items": []}).status_code == 422


def test_so_luong_khong_hop_le(client, tokens, products):
    r = client.post("/orders", headers=tokens["buyer"], json={"items": [{"product_id": products["0110065001"], "quantity": 0}]})
    assert r.status_code == 422


def test_khong_dat_duoc_san_pham_da_ngung_ban(client, tokens, products):
    r = client.post("/orders", headers=tokens["buyer"], json={"items": [{"product_id": products["0111565001"], "quantity": 1}]})
    assert r.status_code == 422


def test_dat_hang_tinh_tien_theo_gia_vnd(client, tokens, products):
    r = client.post("/orders", headers=tokens["buyer"], json={"items": [{"product_id": products["0110065001"], "quantity": 2}]})
    assert r.status_code == 201
    assert r.json()["total_amount"] == 900000
    assert any(o["id"] == r.json()["id"] for o in client.get("/orders/me", headers=tokens["buyer"]).json())


# ---------------------------------------------------------------- gợi ý theo hành vi

def test_goi_y_theo_hanh_vi_va_loai_mon_da_mua(client, tokens, products):
    me = client.get("/users/me", headers=tokens["buyer"]).json()["id"]
    # Chưa có run model → chỉ có gợi ý từ hành vi: xem màu 015 → gợi ý màu 044 cùng product_code
    client.get(f"/products/{products['0108775015']}", headers=tokens["buyer"])
    recs = client.get(f"/predict/{me}?k=5", headers=tokens["buyer"]).json()
    ids = [r["product_id"] for r in recs]
    assert products["0108775044"] in ids
    assert products["0108775015"] not in ids          # món vừa xem không gợi ý lại chính nó
    assert products["0110065001"] not in ids          # món đã mua (test trên) bị loại
    assert [r["rank"] for r in recs] == list(range(1, len(recs) + 1))


# ---------------------------------------------------------------- doanh số

def test_doanh_so_khong_tinh_don_huy(client, tokens, products):
    before = client.get("/dashboard/sales", headers=tokens["admin"]).json()["today"]
    r = client.post("/orders", headers=tokens["buyer"], json={"items": [{"product_id": products["0108775044"], "quantity": 1}]})
    order_id = r.json()["id"]
    after = client.get("/dashboard/sales", headers=tokens["admin"]).json()["today"]
    assert after["orders"] == before["orders"] + 1
    assert after["revenue"] == before["revenue"] + 160000

    client.patch(f"/orders/{order_id}/status?status_value=3", headers=tokens["admin"])   # hủy
    cancelled = client.get("/dashboard/sales", headers=tokens["admin"]).json()["today"]
    assert cancelled["revenue"] == before["revenue"]
    assert cancelled["cancelled_orders"] == before["cancelled_orders"] + 1
