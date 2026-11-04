---
marp: true
theme: default
paginate: true
header: "CO5119 · Intelligent Systems — HUB Personalized Fashion Recommendation"
footer: "Random Forest Ranker on H&M Kaggle Dataset (31.8M Transactions)"
---

# HUB — Hệ thống Gợi ý Thời trang Cá nhân hóa
### Two-Stage Candidate Generation · Random Forest Ranker · Real-time Session Re-ranking

**Đồ án môn Hệ thống Thông minh (Intelligent Systems — CO5119)**
- **Bài toán:** Dự đoán $\text{Top-12}$ sản phẩm thời trang mỗi khách hàng sẽ mua trong 7 ngày tới
- **Dữ liệu thật 100%:** H&M Personalized Fashion Recommendations (Kaggle)
- **Kiến trúc MVP:** React + Vite + TypeScript · FastAPI + SQLAlchemy · Scikit-learn Pipeline

---

## Slide 2: Bài toán Thực tế & Thách thức Khoa học

- **Quy mô dữ liệu lớn & Thưa (Extreme Sparsity):**
  - **31.788.324** giao dịch thực tế · **105.542** sản phẩm · **1.371.980** khách hàng (2018–2020).
  - Không gian tổ hợp: $\sim 1,45 \times 10^{11}$ cặp `(customer, article)` $\rightarrow$ không thể chấm điểm trực tiếp toàn bộ.
- **Đặc thù ngành Thời trang Nhanh (Fast Fashion):**
  - Tính mùa vụ và xu hướng biến đổi theo từng tuần (*non-stationary*).
  - Nhiều biến thể màu sắc trên cùng một mã thiết kế (`product_code`).
- **Bài toán Cold-start kép:**
  - **37,8%** khách hàng trong tuần kiểm tra không có giao dịch ở 8 tuần trước đó.
  - Khách mới đăng ký trên web cần được cá nhân hóa ngay từ những cú click đầu tiên.

---

## Slide 3: Các Bên Liên quan (Actors) & Kiến trúc Tổng thể

| Actor | Tài khoản Demo | Vai trò trong Hệ thống Thông minh |
|---|---|---|
| **👤 Buyer** | `buyer_demo` / `123456` | Mua sắm, nhận gợi ý $\text{Top-12}$, tương tác (xem/giỏ/wishlist/đánh giá sao) kích hoạt Re-ranking tức thời. |
| **🧑‍🔬 Data Scientist** | `ds_demo` / `123456` | Phân tích EDA, cấu hình siêu tham số, kích hoạt huấn luyện trên Kaggle/Local, giám sát $\text{MAP}@12$, kiểm soát ghi đè và phân tích lỗi. |
| **🛡️ Admin** | `kuroisme` / `123456` | Giám sát Dashboard doanh thu/đơn hàng, quản lý danh mục sản phẩm và tài khoản người dùng. |

```
[Kaggle / Local ML Pipeline] ──(summary, recs, catalog, EDA)──▶ [FastAPI Backend + DB] ◀──▶ [React UI (18 màn Figma)]
         ▲                                                             │
         └───────────────(app_events.csv: đơn mua trên web)────────────┘
```

---

## Slide 4: EDA & Chiến lược Chia Dữ liệu Chống Rò rỉ (Anti-Leakage)

- **Chia tập dữ liệu trượt theo thời gian (Sliding Temporal Split):**
  - **Test Week:** `16/09/2020 → 22/09/2020` (7 ngày cuối cùng của dataset).
  - **Validation Week:** `09/09/2020 → 15/09/2020` ($72.019$ khách hàng).
  - **Train Weeks (3 tuần nhãn):** `19/08/2020 → 08/09/2020`.
- **Nguyên tắc Chống Rò rỉ Dữ liệu (Zero Temporal Leakage):**
  - Mọi đặc trưng và nguồn ứng viên của tuần bắt đầu tại $t_0$ chỉ được tính từ giao dịch trong cửa sổ 8 tuần **trước** $t_0$: $t_{\text{dat}} \in [t_0 - 56\text{ ngày}, t_0)$.
  - Được bảo chứng bằng Unit Test tự động: `test_feature_khong_doi_khi_them_du_lieu_tuong_lai`.

![bg right:42% fit](data_scientist/runs/run_20261022_150442/reports/normalized/3_3_1_time_split.png)

---

## Slide 5: Giai đoạn 1 — Sinh Ứng viên & 32 Đặc trưng (Feature Engineering)

### 1. Thu hồi 100 ứng viên/khách từ 5 nguồn ưu tiên (`SOURCE_PRIORITY`):
1. **Mua lại (`src_repurchase`, w=16):** Sản phẩm khách từng mua gần nhất.
2. **Mua kèm giỏ hàng (`src_copurchase`, w=8):** Cặp sản phẩm mua cùng ngày trong 14 ngày qua.
3. **Cùng thiết kế khác màu (`src_samecode`, w=4):** Biến thể bán chạy cùng `product_code`.
4. **Bán chạy theo nhóm tuổi (`src_agebest`, w=2):** Top bán chạy trong nhóm tuổi `[0, 25, 35, 45, 55, 200]`.
5. **Bán chạy toàn cục (`src_bestseller`, w=1):** Xu hướng chung toàn sàn.

### 2. Vector 32 Đặc trưng cho mỗi cặp `(customer, article)`:
- **Khách hàng (6):** `c_n_tx`, `c_n_articles`, `c_days_since_last`, `c_avg_price`, `c_online_ratio`, `c_age`.
- **Sản phẩm (14):** `a_cnt_window`, `a_cnt_1w`, `a_n_customers`, `a_avg_price`, `a_days_since_first`, `pg_code` + 8 thuộc tính tĩnh.
- **Tương tác Cặp (7):** `ca_cnt`, `ca_days_since`, `c_group_share`, `c_code_cnt`, `price_diff`, `bestseller_rank`, `agebest_rank`.
- **Cờ Nguồn (5):** 5 biến nhị phân tương ứng 5 nguồn ứng viên.

---

## Slide 6: Giai đoạn 2 & 3 — Random Forest Ranker + Online Session Re-ranking

### Offline Ranker (`hub_pipeline.py`)
- **Mô hình:** `RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_leaf=5)`.
- **Lấy mẫu âm (Negative Downsampling 1:5):** Từ $14,63$ triệu dòng ứng viên $\rightarrow$ lấy $100\%$ mẫu dương + $5\times$ mẫu âm = **$398.166$ dòng huấn luyện**.
- **Chấm điểm xác suất:** Sắp xếp theo $\hat{p}(y=1 \mid u, i)$ xuất $\text{Top-50}$ ứng viên/khách vào bảng `user_recommendations`.

### Online Session Re-ranking (`session_rerank.py` tại API `/predict`)
- Kết hợp điểm Random Forest với tín hiệu tức thời trong phiên (bán rã mũ $\text{half-life} = 3\text{ ngày}$):
  $$\text{Score}(u, i) = \text{Score}_{\text{RF}}(u, i) + 0.25 \sum_{a \in \mathcal{A}_u} w(a) \cdot 0.5^{\Delta t(a) / 3} \cdot \text{Sim}(i, a) - \text{Penalty}_{\le 2\star}(i)$$
  với trọng số: `VIEWED = +1.0`, `CART = +2.5`, `WISHLIST = +3.0`, `REMOVE_CART = -1.0`, `REMOVE_WISHLIST = -2.0`.
- Loại bỏ món đã mua, món đánh giá $\le 2$ sao và giới hạn **tối đa 1 màu cho mỗi `product_code`**.

---

## Slide 7: Kết quả Thực nghiệm & Ablation Study (72.019 Khách Validation)

| Cấu hình Thực nghiệm | Dòng Train | Candidate Recall | Val MAP@12 | Val Recall@12 | Val NDCG@12 | Test MAP@12 |
|---|---:|---:|---:|---:|---:|---:|
| **BL1 · Top-12 Bán chạy tuần** | — | — | `0.00660` | `2.09%` | `0.01260` | `0.00875` |
| **BL2 · Mua lại gần nhất (+Bestseller)** | — | — | `0.02498` | `4.91%` | `0.03592` | `0.02625` |
| **RF · Lấy mẫu 10% khách (4w hist)** | $7.386$ | `5.27%` | `0.02770` | `5.61%` | `0.04036` | `0.02904` |
| **RF · Toàn bộ khách (1 tuần nhãn)** | $89.886$ | `6.17%` | `0.02961` | `5.93%` | `0.04289` | `0.03031` |
| **RF · Mở rộng cỡ nguồn ứng viên** | $136.458$ | `9.43%` | `0.02987` | `6.23%` | `0.04394` | `0.03098` |
| **RF · 3 Tuần nhãn (Mô hình cuối)** | **$398.166$** | **`9.43%`** | **`0.03014`** | **`6.27%`** | **`0.04430`** | **`0.03104`** |

- **Vượt trội so với Baseline:** Tăng **+20,66% MAP@12** và **+23,33% NDCG@12** trên Validation so với Baseline mạnh nhất ($\text{BL2}$); gấp **4,56 lần** so với gợi ý bán chạy ($\text{BL1}$).
- **Top-3 Đặc trưng quan trọng nhất:** `ca_days_since` (**17,42%**), `a_cnt_1w` (**8,96%**), `ca_cnt` (**7,47%**).

---

## Slide 8: Phân tích Lỗi (Error Analysis) & Bài học Khoa học

1. **Hiệu năng theo Phân khúc Khách hàng:**
   - **Cold start ($37,8\%$ khách):** $\text{MAP}@12 = \mathbf{0.00818}$ (cao hơn $\text{BL1}$ nhờ nguồn bán chạy theo nhóm tuổi `src_agebest`).
   - **Khách có lịch sử ($\ge 1$ giao dịch, $62,2\%$ khách):** $\text{MAP}@12$ nhảy vọt lên **$\mathbf{0.0427 \rightarrow 0.0449}$** ($\text{Recall}@12$ lên tới **$9,51\%$**).
2. **Nút thắt Độ phủ Ứng viên (Candidate Recall Bottleneck):**
   - 100 ứng viên/khách thu hồi được **$9,43\%$ (Val)** và **$10,07\%$ (Test)** tổng giao dịch thực tế.
   - Riêng bộ xếp hạng Random Forest đã giữ lại được **$6,27\% / 9,43\% \approx 66,5\%$** lượng sản phẩm đúng vào trong Top-12!
3. **Hiệu năng theo Nhóm Sản phẩm:**
   - Tốt nhất ở trang phục chính: *Garment Lower body* ($\text{Recall}@12 = 8,11\%$), *Garment Upper body* ($4,54\%$).
   - Thấp nhất ở *Accessories* ($\text{Recall}@12 = 0,83\%$) do tính chất mua ngẫu hứng.

---

## Slide 9: Kịch bản Live Demo Trực tiếp (5 Phút Bảo vệ)

### Bước 1: Khởi động Hệ thống (Terminal)
```powershell
conda activate hub
npm run dev   # Chạy đồng thời Backend (port 8000) & Frontend (port 5173)
```

### Bước 2: Demo Vai trò Data Scientist (`ds_demo` / `123456`)
1. **Màn hình EDA & Tiền xử lý:** Trình diễn 10 biểu đồ phân phối gốc & sau chuẩn hóa + thẻ Xu hướng tuần cuối.
2. **Màn hình Model Metrics:** Chỉ rõ bảng đối sánh Random Forest (`MAP@12 = 0.0301`) vượt xa Baseline 1 (`0.0066`) và Baseline 2 (`0.0250`).
3. **Màn hình Phân tích lỗi:** Trình diễn biểu đồ Cold-start vs Active, Feature Importance và Candidate Recall.
4. **Màn hình Lịch chạy & Huấn luyện:** Giải thích cấu hình siêu tham số RF, lịch chạy tự động 02:00 và cơ chế bảo vệ khi model kém hơn baseline.

### Bước 3: Demo Vai trò Buyer (`buyer_demo` / `123456`) & Admin (`kuroisme` / `123456`)
1. **Buyer — Trang chủ:** Xem 12 sản phẩm gợi ý cá nhân hóa từ Random Forest.
2. **Buyer — Re-ranking Tức thời:** Click vào 1 chiếc đầm/áo khoác $\rightarrow$ bấm **Thêm vào Wishlist** $\rightarrow$ quay lại Trang chủ: thấy ngay các sản phẩm cùng loại/cùng mã khác màu được đẩy lên đầu!
3. **Buyer — Đặt hàng & Phản hồi:** Đặt mua 1 sản phẩm $\rightarrow$ sản phẩm đó lập tức biến mất khỏi danh sách gợi ý.
4. **Admin — Dashboard:** Đăng nhập `kuroisme` kiểm tra đơn hàng vừa tạo và biểu đồ doanh thu cập nhật tức thời.

---

## Slide 10: Bộ Câu hỏi & Trả lời Phản biện (Q&A Defense Cheat Sheet — Phần 1)

**❓ Câu 1: Tại sao nhóm chọn Random Forest làm Ranker mà không dùng Collaborative Filtering (Matrix Factorization / kNN) đơn thuần?**
> **Trả lời:** Matrix Factorization hoặc User-Item kNN thuần túy gặp 2 hạn chế lớn trên tập H&M: (1) Ma trận $1,37\text{M} \times 105\text{K}$ quá thưa và tính mùa vụ thời trang thay đổi từng tuần làm ma trận phân rã nhanh chóng lỗi thời; (2) Khó tích hợp đồng thời các đặc trưng liên tục như khoảng cách ngày mua (`ca_days_since`), độ lệch giá (`price_diff`) và nhóm tuổi. Với kiến trúc **Two-Stage**, bước 1 đã thu hồi ứng viên bằng Co-purchase (bản chất là Item-Item CF), còn bước 2 dùng **Random Forest** kết hợp cả tín hiệu CF lẫn 32 đặc trưng nội dung & thời gian, giúp tăng $+20,7\%$ $\text{MAP}@12$ so với chỉ dùng lịch sử mua lại.

**❓ Câu 2: Làm sao nhóm đảm bảo hoàn toàn không bị Data Leakage (rò rỉ dữ liệu) khi tạo 32 features?**
> **Trả lời:** Trong `hub_pipeline.py`, hàm `week_dataset(tx, ..., start)` tách biệt hoàn toàn: nhãn (`labels_for`) chỉ lấy trong $[start, start + 7\text{ ngày})$, còn lịch sử (`history_for`) chỉ lấy nghiêm ngặt $t_{\text{dat}} < start$. Hơn nữa, nhóm đã viết kiểm thử tự động `test_feature_khong_doi_khi_them_du_lieu_tuong_lai` trong `test_pipeline.py`: chèn thêm giao dịch vào tuần nhãn rồi tính lại toàn bộ 32 features, kết quả ma trận đặc trưng không thay đổi bất kỳ con số nào.

---

## Slide 11: Bộ Câu hỏi & Trả lời Phản biện (Q&A Defense Cheat Sheet — Phần 2)

**❓ Câu 3: Tại sao chỉ số $\text{MAP}@12 \approx 0.0301$ nghe có vẻ nhỏ? Con số này có ý nghĩa gì trên bảng xếp hạng Kaggle H&M?**
> **Trả lời:** Trong bài toán dự đoán chính xác mặt hàng thời trang khách sẽ mua trong 7 ngày tới trên kho $105.542$ sản phẩm mà không biết trước ngân sách hay nhu cầu đột xuất của khách, xác suất đoán ngẫu nhiên chỉ là $\sim 10^{-5}$. Trên cuộc thi Kaggle H&M, Baseline bán chạy toàn cục chỉ đạt `0.0066`, và các giải pháp Top Leaderboard thế giới dao động quanh mức `0.030 – 0.036`. Mức `0.03014` (Val) và `0.03104` (Test) của hệ thống là kết quả rất cạnh tranh và thực tế.

**❓ Câu 4: Khi một khách hàng hoàn toàn mới đăng ký trên web (Cold-start User), hệ thống gợi ý hoạt động như thế nào?**
> **Trả lời:** Hệ thống xử lý ở 2 lớp:
> 1. **Lớp Offline:** Nếu biết tuổi của khách, nguồn `src_agebest` gợi ý các sản phẩm bán chạy nhất trong đúng độ tuổi đó; nếu chưa biết tuổi thì dùng `bestsellers.json`.
> 2. **Lớp Online (`session_rerank.py`):** Ngay khi khách vừa click xem 1 sản phẩm hoặc thêm vào giỏ/wishlist, hệ thống lập tức lấy các sản phẩm cùng `product_code` và cùng `product_type_name` bán chạy nhất cộng điểm ưu tiên theo hàm bán rã thời gian $0.5^{\Delta t / 3.0}$, giúp cá nhân hóa tức thì mà không cần chờ huấn luyện lại vào lúc 02:00 sáng.

---

## Slide 12: Tổng kết & Đóng góp của Đồ án

- **Đáp ứng 100% tiêu chí Rubric môn Intelligent Systems:**
  - **Dữ liệu thật 100%** (H&M Kaggle 31,8M giao dịch), xử lý tối ưu bộ nhớ và chống rò rỉ dữ liệu tuyệt đối.
  - **Mô hình Học máy thực chất:** Two-stage Candidate Generation + Random Forest Ranker (32 features) vượt Baseline $+20,66\%$.
  - **Hệ thống MVP hoàn chỉnh:** 3 Roles (Buyer, Admin, Data Scientist), 18 màn hình chuẩn Figma, tích hợp Online Session Re-ranking và vòng lặp phản hồi khép kín.
  - **Chất lượng phần mềm:** Vượt qua **27/27 bài kiểm thử tự động (`pytest`)** và kiểm tra kiểu tĩnh TypeScript (`npm run build`).

