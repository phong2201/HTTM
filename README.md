# HUB — Hệ thống gợi ý thời trang (Random Forest ranker)

Đồ án môn Intelligent Systems (CO5119). Web thương mại điện tử thời trang có gợi ý cá nhân hóa:
**Random Forest** xếp hạng ứng viên sản phẩm cho từng khách, huấn luyện trên dữ liệu thật
**H&M Personalized Fashion Recommendations (Kaggle)**, tích hợp vào hệ thống qua API và giao diện web.

| | |
|---|---|
| Bài toán | Dự đoán 12 sản phẩm mỗi khách sẽ mua trong tuần tới (Top-12 recommendation) |
| Thuật toán chính | Random Forest (scikit-learn) làm **ranker** cho tập ứng viên |
| Dữ liệu | [H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data) — 31,8 triệu giao dịch, 105.542 sản phẩm, 1,37 triệu khách (2018-09-20 → 2020-09-22). **Không dùng dữ liệu mô phỏng.** |
| Actor | **Buyer** (mua sắm, nhận gợi ý), **Admin** (quản lý user/sản phẩm/đơn, dashboard), **Data Scientist** (EDA, cấu hình & huấn luyện, đánh giá, phân tích lỗi, lịch cập nhật) |
| Thành phần | `front-end/` React + Vite · `backend/` FastAPI + SQLAlchemy · `data_scientist/hm_pipeline/` pipeline ML chạy trên Kaggle hoặc local |
| Tài liệu & Sản phẩm nộp bài | 📕 **[Báo cáo PDF Tiếng Anh (REPORT_INTELLIGENT_SYSTEMS_HUB.pdf)](REPORT_INTELLIGENT_SYSTEMS_HUB.pdf)** · 📘 **[Báo cáo PDF Tiếng Việt (REPORT_INTELLIGENT_SYSTEMS_HUB_VI.pdf)](REPORT_INTELLIGENT_SYSTEMS_HUB_VI.pdf)** · 🎬 **[Video Demo Full HD 1080p](DEMO_INTELLIGENT_SYSTEMS_HUB_1080P.mp4)** · 📄 **[Báo cáo Markdown (docs/reports/)](docs/reports/REPORT_HCMUT_STANDARD.md)** · 📊 **[Slide Thuyết trình (docs/slides/SLIDES.md)](docs/slides/SLIDES.md)** · 🎨 **[Đặc tả UI (docs/specs/HUB_UI_SPEC.md)](docs/specs/HUB_UI_SPEC.md)** |

---

## 1. Chạy hệ thống

Yêu cầu: Node.js ≥ 18, Anaconda/Miniconda.

```powershell
# Lần đầu: cài thư viện Node + tạo env conda "hub" (Python 3.11, pandas, scikit-learn, FastAPI…)
npm run setup

# Mỗi lần chạy: backend (http://127.0.0.1:8000) + frontend (http://localhost:5173) song song
conda activate hub
npm run dev
```

| Lệnh | Việc |
|---|---|
| `npm run dev:be` / `npm run dev:fe` | Chỉ chạy backend / frontend |
| `npm test` | Chạy bộ kiểm thử (API + pipeline ML) |
| `npm run build` | Kiểm tra type + build frontend |

Backend đọc `backend/.env` (đã có sẵn, dùng SQLite `backend/recommendation_system.db`):

```env
DATABASE_URL=sqlite:///./recommendation_system.db
SECRET_KEY=dev-secret-change-me
```

Dùng Postgres: dựng bảng từ `backend/scripts.sql` (sinh tự động từ model) rồi đổi `DATABASE_URL`.

**Tài khoản có sẵn** (chọn đúng tab role ở màn đăng nhập):

| Role | Username | Mật khẩu |
|---|---|---|
| Admin | `kuroisme` | `123456` |
| Data Scientist | `ds_demo` | `123456` |
| Buyer | `buyer_demo` | `123456` (hoặc tự đăng ký) |

## 2. Truy cập dữ liệu

Dataset thuộc cuộc thi Kaggle, cần tài khoản Kaggle:

1. Vào [trang cuộc thi](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) → **Join Competition** (chấp nhận điều khoản).
2. Kaggle → Settings → API → **Create Legacy API Key** → chép `kaggle.json` vào `C:\Users\<bạn>\.kaggle\kaggle.json`.
3. Không cần tải 35 GB về máy: pipeline chạy **trên Kaggle**, dataset gắn sẵn vào kernel. Backend tự đẩy script, chờ chạy xong, tải kết quả về.
4. (Tùy chọn, chạy local) tải 3 file CSV vào `data/hm/`:
   ```powershell
   kaggle competitions download -c h-and-m-personalized-fashion-recommendations -f transactions_train.csv -p data/hm
   ```
   (tương tự cho `articles.csv`, `customers.csv`, rồi giải nén).

Cột dùng: `articles.csv` (article_id, product_code, prod_name, product_type_name, product_group_name, colour_group_name,
graphical_appearance_name, index_group_name, detail_desc), `customers.csv` (customer_id, age),
`transactions_train.csv` (t_dat, customer_id, article_id, price, sales_channel_id), `images/` (ảnh sản phẩm hiển thị trên web).

## 3. Kiến trúc & luồng dữ liệu

```
                ┌───────────── Kaggle (dataset H&M cố định + dataset hub-app-events) ─────────────┐
                │  hub_pipeline.py: chia theo thời gian → sinh ứng viên → feature → Random Forest   │
                │  → đánh giá vs baseline → xuất gợi ý, catalog, metrics, phân tích lỗi, ảnh EDA    │
                └──────────────▲─────────────────────────────────────────────┬───────────────────┘
       kaggle kernels push     │ đơn mua trên web (cửa sổ N tuần)             │ kaggle kernels output
                               │                                              ▼
 React (Buyer/Admin/DS) ◀──▶ FastAPI ──────────────────────────────▶ DB: products, user_recommendations,
                                │  /predict: đọc gợi ý tính sẵn                orders, interactions, sales_daily…
                                │  + sắp xếp lại theo hành vi trong phiên (xem / wishlist / giỏ / mua / đánh giá)
                                └─ lịch 02:00 mỗi ngày · tổng hợp doanh số · chốt sổ tháng/năm
```

- Gợi ý **tính sẵn** mỗi đêm và ghi vào `user_recommendations`; API chỉ đọc bảng này (+ lớp sắp xếp lại theo hành vi tức thời).
- Data Scientist điều khiển toàn bộ vòng đời ở màn **Lịch chạy**: nơi chạy (Kaggle/local), dữ liệu (lấy mẫu/toàn bộ), tham số RF, Train AI, xử lý ngoại lệ (kết quả kém baseline → chọn ghi đè hoặc giữ bản cũ).
- Chi tiết pipeline: [data_scientist/hm_pipeline/README.md](data_scientist/hm_pipeline/README.md).

## 4. Quy trình ML

| Bước | Nội dung |
|---|---|
| Tiền xử lý | Đọc CSV theo chunk, chỉ giữ cửa sổ thời gian cần thiết; `customer_id` (64 hex) → int64; ép kiểu `int32/float32`; giá chuẩn hóa giữ nguyên trong model (web quy đổi ước lượng sang VND để hiển thị) |
| Chia dữ liệu | **Theo thời gian**: test = tuần cuối (16–22/09/2020), val = tuần trước đó, train = 3 tuần nhãn liền trước. Feature của mỗi tuần nhãn chỉ tính từ giao dịch **trước** tuần đó (8 tuần) |
| Chống rò rỉ | Không có feature nào nhìn dữ liệu sau cutoff — có kiểm thử tự động (`test_feature_khong_doi_khi_them_du_lieu_tuong_lai`). Đơn trên web chỉ dùng cho bước tạo gợi ý cuối, không vào train/val/test |
| Ứng viên | Mua lại, bán chạy tuần, bán chạy theo nhóm tuổi, cùng product_code (màu khác), co-purchase |
| Feature | 32 feature: hành vi khách (số giao dịch, độ gần, giá TB, tỉ lệ online, tuổi), sản phẩm (độ phổ biến, giá, thuộc tính), cặp khách×sản phẩm (đã mua bao nhiêu lần, cách đây bao lâu, độ hợp nhóm), cờ nguồn ứng viên |
| Huấn luyện | `RandomForestClassifier` (200 cây, max_depth 12, min_samples_leaf 5), lấy mẫu âm 1:5 |
| Đánh giá | MAP@12 (metric chính thức của cuộc thi), Recall@12, Precision@12, NDCG@12, recall ứng viên; so với 2 baseline: **BL1** top-12 bán chạy tuần, **BL2** mua lại gần nhất |

### Kết quả (toàn bộ khách, 72.019 khách ở tuần val)

| Lần chạy | Dòng train | MAP@12 val | MAP@12 test |
|---|---|---|---|
| BL1 · top-12 bán chạy | — | 0.0066 | — |
| BL2 · mua lại gần nhất | — | 0.0250 | — |
| RF · lấy mẫu 10% khách | 7.386 | 0.0277 | — |
| RF · toàn bộ khách | 89.886 | 0.0296 | 0.0303 |
| RF · mở rộng ứng viên | 136.458 | 0.0299 | 0.0310 |
| **RF · 3 tuần nhãn** | **398.166** | **0.0301** | **0.0310** |

Random Forest cao hơn baseline mạnh nhất ~20%. Phân tích lỗi (màn **Phân tích lỗi**): recall ứng viên 9,4% là giới hạn trên của ranker;
khách cold start (38%) chỉ đạt MAP@12 ≈ 0.008 so với ≈ 0.044 của khách có lịch sử; nhóm Accessories gợi ý kém nhất.

## 5. Kiểm thử

`npm test` — 27 kiểm thử (`backend/tests/`), chạy trên DB tạm:
xác thực & phân quyền theo role, kiểm tra đầu vào (thiếu trường, số lượng ≤ 0, id sai định dạng, cấu hình ngoài miền, sản phẩm ngừng bán),
luồng đặt hàng & tính tiền, gợi ý theo hành vi, doanh số loại đơn hủy; công thức MAP/NDCG, chia theo thời gian, chống rò rỉ, lấy mẫu cố định.

## 6. Giới hạn

- Dataset H&M là dữ liệu **lịch sử cố định** (dừng 22/09/2020); đơn trên web được dời về cuối dataset (giữ khoảng cách thời gian) khi tạo gợi ý.
- Giá trong dataset đã chuẩn hóa, Kaggle không công bố hệ số → giá VND trên web là **quy đổi ước lượng** (`HM_PRICE_TO_VND` trong `backend/core/config.py`).
- Tài khoản web được gán một `customer_id` H&M có lịch sử thật để có gợi ý; hành vi trên web chỉ bổ sung, không thay thế lịch sử đó.
- Random Forest của scikit-learn chạy CPU; Kaggle cấp 4 nhân → một lần chạy toàn bộ khách mất ~20–30 phút (chưa kể thời gian Kaggle xếp hàng).
- Không có ảnh cho ~0,2% sản phẩm (dataset thiếu ảnh) → web hiển thị ô thay thế.

## 7. Cấu trúc thư mục dự án

```
HTTM/
├── DEMO_INTELLIGENT_SYSTEMS_HUB_1080P.mp4   # 🎬 Video Demo Toàn diện Full HD 1080p (~5 phút)
├── REPORT_INTELLIGENT_SYSTEMS_HUB.pdf       # 📕 Báo cáo học thuật tiếng Anh (chuẩn LaTeX/arXiv)
├── REPORT_INTELLIGENT_SYSTEMS_HUB_VI.pdf    # 📘 Báo cáo BTL tiếng Việt hoàn chỉnh
├── README.md                                # Hướng dẫn tổng quan & khởi chạy hệ thống
├── package.json                             # Lệnh npm root: setup, dev, test, build
├── environment.yml                          # Môi trường Conda "hub" (Python 3.11, PyTorch, scikit-learn)
│
├── backend/                                 # Dịch vụ Backend FastAPI + SQLAlchemy
│   ├── main.py                              # Khởi tạo app, đăng ký router, phục vụ ảnh tĩnh
│   ├── database.py                          # Kết nối cơ sở dữ liệu
│   ├── core/                                # Cấu hình (config.py), Bảo mật JWT (security.py)
│   ├── dependencies/                        # RBAC middleware kiểm tra quyền truy cập theo role
│   ├── routers/                             # Endpoints: auth, products, cart, order, wishlist, feedback, recommendation, dashboard
│   ├── services/                            # hm_pipeline_service.py điều phối, session_rerank.py tái xếp hạng
│   ├── models/                              # SQLAlchemy ORM Models
│   └── tests/                               # Bộ unit test & integration test pytest
│
├── front-end/                               # Giao diện Web SPA (React 18 + Vite + TypeScript)
│   └── src/
│       ├── app/                             # routes.tsx (phân quyền RBAC), components/ui
│       ├── pages/                           # buyer/, admin/, data-science/, auth/
│       ├── context/                         # AuthContext (JWT session), ShopContext (Cart & Wishlist)
│       └── services/api.ts                  # Axios client kết nối FastAPI gateway
│
├── data_scientist/                          # Pipeline Khoa học Dữ liệu & Học máy (MLOps)
│   ├── hm_pipeline/                         # hub_pipeline.py: Two-stage Random Forest pipeline
│   └── notebooks/                           # Notebooks phân tích EDA 31.78M giao dịch Kaggle
│
├── docs/                                    # Toàn bộ tài liệu báo cáo, sơ đồ & đặc tả
│   ├── reports/                             # REPORT_HCMUT_STANDARD.md, REPORT_HCMUT_TIENG_VIET.md, REPORT.md
│   ├── diagrams/                            # Bản thiết kế Excalidraw (01_architecture, 02_usecase, 03_pipeline, 04_rerank)
│   ├── report_assets/                       # 16+ hình ảnh biểu đồ phân tích dữ liệu và sơ đồ kiến trúc
│   ├── specs/                               # Đặc tả giao diện chi tiết (HUB_UI_SPEC.md)
│   └── slides/                              # Slide thuyết trình bảo vệ đồ án (SLIDES.md)
│
└── scripts/                                 # Bộ công cụ tự động hóa & kết xuất
    ├── reports/                             # generate_pdf_report.py, generate_pdf_report_vi.py
    ├── video/                               # record_demo_video_1080p_extended.js (kịch bản quay Playwright)
    ├── tests/                               # run_ui_tests.js (kiểm thử giao diện)
    └── patches/                             # Các công cụ hỗ trợ chuẩn hóa ký tự toán học & định dạng
```

## 8. Quy trình vận hành

1. **Cài đặt & khởi động** — `npm run setup` (lần đầu) → `conda activate hub` → `npm run dev`.
2. **Huấn luyện** — đăng nhập **Data Scientist** → **Lịch chạy** → chọn nơi chạy (Kaggle / local), phạm vi dữ liệu,
   tham số Random Forest → **Train AI**. Hoặc để lịch tự chạy lúc 02:00 mỗi ngày.
3. **Chạy pipeline** — backend đẩy `hub_pipeline.py` lên Kaggle (hoặc chạy local với `data/hm/`), theo dõi
   `progress.json` qua 6 bước: chọn subset & chia theo thời gian → sinh ứng viên → tạo feature → huấn luyện Random Forest
   → đánh giá vs baseline → ghi bảng Recommendations.
4. **Nạp kết quả** — kết quả tải về `data_scientist/runs/<run_id>/`; backend nạp catalog + ảnh vào `products`,
   gợi ý vào `user_recommendations`, metrics / phân tích lỗi / xu hướng cho các màn Data Science.
   Nếu MAP@12 thấp hơn baseline, Data Scientist chọn **Vẫn ghi đè** hoặc **Giữ bản cũ**.
5. **Phục vụ gợi ý** — Buyer mở web → `/predict` đọc gợi ý tính sẵn → sắp xếp lại theo hành vi trong phiên
   (xem, wishlist, giỏ, mua, đánh giá).
6. **Vòng phản hồi** — đơn mua trên web được gửi kèm lần chạy kế tiếp để cập nhật gợi ý; Admin theo dõi doanh số
   và đơn hàng ở Dashboard.
7. **Kiểm thử** — `npm test` trước khi commit.
