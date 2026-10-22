# Pipeline H&M · Random Forest ranker

`hub_pipeline.py` là một script duy nhất, chạy được trên **Kaggle** (dataset gắn sẵn) hoặc **máy local**.
Backend (`backend/services/hm_pipeline_service.py`) điều phối việc chạy và nạp kết quả vào DB.

## Chuẩn bị (một lần)

1. Kaggle → cuộc thi [H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) → **Join Competition**.
2. Kaggle → Settings → API → **Create New Token** → chép `kaggle.json` vào `C:\Users\<bạn>\.kaggle\kaggle.json`.
3. `conda activate hub` (xem `environment.yml` ở thư mục gốc).

## Chạy

Từ web: đăng nhập **Data Scientist** → **Lịch chạy** → chọn *Chạy trên* (Kaggle / Máy local) → **Train AI**.
Mặc định backend tự chạy lúc **02:00** mỗi ngày (bật/tắt ở cùng màn hình; máy chạy backend phải đang bật).

| Nơi chạy | Cần gì | Ghi chú |
|---|---|---|
| Kaggle | `kaggle.json` | Backend `kaggle kernels push` → chờ → `kaggle kernels output` về `data_scientist/runs/<run_id>/`. Kernel tên `<username>/hub-rf-pipeline` (riêng tư). |
| Local | 3 file CSV trong `data/hm/` | Chọn *Lấy mẫu khách* nếu RAM 16 GB. |

Chạy tay ở local (không qua backend):

```bash
python data_scientist/hm_pipeline/hub_pipeline.py --data-dir data/hm --out data_scientist/runs/run_tay
```

Rồi nạp vào DB: `POST /ai/runs/run_tay/import` (tài khoản Data Scientist). Cách này cũng dùng được khi bạn
chạy notebook trực tiếp trên giao diện Kaggle: tải output về, giải nén vào `data_scientist/runs/<tên>/`, gọi import.

## Kết quả mỗi run (`data_scientist/runs/<run_id>/`)

| File | Dùng ở |
|---|---|
| `summary.json` | Model metrics (MAP/Recall/Precision/NDCG@12, baseline, chia thời gian) |
| `error_analysis.json` | Phân tích lỗi + thẻ "Tối ưu hóa gợi ý" |
| `insights.json` | Thẻ "Xu hướng sản phẩm" (tuần cuối so với tuần trước) |
| `recommendations.csv` | Top 50 gợi ý/khách cho ~300 khách hoạt động nhất → gán cho tài khoản Buyer |
| `catalog.csv`, `images/` | Sản phẩm H&M nạp vào bảng `products` |
| `bestsellers.json` | `GET /products/best-sellers` |
| `reports/original`, `reports/normalized` | Ảnh EDA (màn Data Science) |
| `progress.json` | Tiến trình 6 bước |

Khi nạp, sản phẩm của dataset cũ (Myntra) bị **ẩn** (`is_active = false`), không bị xóa vì đơn hàng cũ còn tham chiếu.
Run có MAP@12 thấp hơn baseline sẽ **không** tự ghi đè Recommendations — chọn "Vẫn ghi đè" hoặc "Giữ bản cũ" ở màn Lịch chạy.
