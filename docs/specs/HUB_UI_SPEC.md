# HUB — Đặc tả UI để code theo Figma

> File này dành cho Claude (VS Code) đọc và làm theo khi sửa frontend trong repo `intelligent-system`.
> Nguồn thiết kế: Figma **https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK** (page "Màn hình", 18 frame).
> Nếu có Figma MCP, lấy chi tiết từng màn bằng `fileKey = aVpxn31dow3jmdT2vveAGK` và `nodeId` trong bảng ở mục 4.

---

## Liên kết

| Tài nguyên | Link |
|---|---|
| Figma (toàn bộ thiết kế) | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK |
| Dataset H&M (tổng quan cuộc thi) | https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/overview |
| Dataset H&M (trang tải dữ liệu) | https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data |
| Repo code | https://github.com/tinletrongCS/intelligent-system |

> Tải dataset: đăng nhập Kaggle → bấm **Join Competition** → tab **Data**. Gồm `articles.csv`, `customers.csv`, `transactions_train.csv`, `sample_submission.csv`, thư mục `images/` (ảnh theo `article_id`, rất nặng — có thể chỉ tải CSV trước).
> Hoặc dùng CLI: `kaggle competitions download -c h-and-m-personalized-fashion-recommendations`

### Link Figma từng màn hình

| # | Màn | Link |
|---|---|---|
| 01 | Đăng nhập | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=43-3 |
| 02 | Đăng ký | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=43-46 |
| 03 | Trang chủ | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=43-86 |
| 04 | Sản phẩm (tìm kiếm & lọc) | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=44-2 |
| 05 | Chi tiết sản phẩm | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=44-396 |
| 06 | Wishlist | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=44-540 |
| 07 | Giỏ hàng (drawer) | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=45-2 |
| 08 | Thanh toán | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=45-248 |
| 09 | Lịch sử đơn hàng | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=45-378 |
| 10 | Trạng thái rỗng & lỗi | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=45-456 |
| 11 | Admin · Người dùng | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=46-3 |
| 12 | Admin · Sản phẩm | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=46-166 |
| 13 | Admin · Đơn hàng | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=46-367 |
| 14 | Dashboard quản trị | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=46-483 |
| 15 | Data Science · EDA & tiền xử lý | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=47-3 |
| 16 | Data Science · Model metrics | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=47-146 |
| 17 | Data Science · Lịch chạy & huấn luyện | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=47-320 |
| 18 | Data Science · Phân tích lỗi | https://www.figma.com/design/aVpxn31dow3jmdT2vveAGK?node-id=47-463 |

### Cột dữ liệu H&M dùng trên giao diện

| File | Cột | Hiển thị ở |
|---|---|---|
| `articles.csv` | `article_id`, `product_code`, `prod_name` | Mã, tên sản phẩm (mọi màn) |
| | `product_type_name` | "Loại" trên thẻ & chi tiết |
| | `product_group_name` | Bộ lọc "Nhóm sản phẩm", phân tích lỗi |
| | `colour_group_name` | Bộ lọc "Màu sắc", chi tiết |
| | `graphical_appearance_name` | "Họa tiết" ở chi tiết |
| | `index_group_name` | Danh mục: Ladieswear, Menswear, Baby/Children, Sport, Divided |
| | `detail_desc` | Mô tả ở chi tiết |
| `customers.csv` | `customer_id` | Liên kết tài khoản Buyer demo (Admin · Người dùng) |
| `transactions_train.csv` | `t_dat`, `article_id`, `price`, `sales_channel_id` | Lịch sử mua, giá trung bình, bán chạy tuần, nhãn huấn luyện |
| `images/` | ảnh theo `article_id` | Ảnh sản phẩm; thiếu ảnh → placeholder |

---

## 0. Bối cảnh & ràng buộc (đọc trước)

- Đồ án môn Intelligent Systems: web gợi ý sản phẩm thời trang, **Random Forest làm ranker**, dữ liệu **H&M Personalized Fashion Recommendations (Kaggle)**.
- **Không dùng dữ liệu giả lập.** Mọi số liệu metrics / thống kê hiển thị phải lấy từ API; khi chưa có thì hiện `—`, không bịa số.
- Tên thương hiệu: **HUB** (thay cho "ShopVN" đang có trong repo).
- Bám **sơ đồ kiến trúc gốc**: 3 actor có giao diện là **Buyer, Admin, Data Scientist**. Không có Seller.
- Gợi ý được **tính sẵn** (bảng `Recommendations`, cập nhật lúc 02:00). API gợi ý chỉ đọc bảng này.
- Giá trong H&M là **giá đã chuẩn hóa** (vd `0.0136`), không phải VND. Không hiển thị `₫`, không có giảm giá.

### Phạm vi việc cần làm
1. Đổi giao diện frontend (`front-end/src`) theo Figma: màu, chữ, layout, tên.
2. Giữ nguyên cách gọi API hiện có trong `src/services/api.ts`; chỉ thêm hàm khi màn hình cần mà chưa có (ghi rõ ở mục 4).
3. **Không** sửa backend trong lượt này, trừ khi được yêu cầu riêng.

---

## 1. Design tokens

### Màu (thay vào `src/styles/theme.css`, giữ tên biến shadcn)

| Token Figma | Hex | Dùng cho | Biến CSS đề xuất |
|---|---|---|---|
| accent / primary | `#E8112D` | Nút chính, logo, link active, giá, badge điểm | `--primary`, `--destructive` giữ riêng |
| accentSoft | `#FFE3E8` | Nền section nổi bật, tab active nhạt, chip lọc | `--accent` |
| canvas | `#FFF3F5` | Nền phụ ánh hồng | — |
| subtle | `#F6F2F3` | Nền trang (body) | `--background` của layout |
| surface / bg | `#FFFFFF` | Card, header, input | `--card`, `--popover` |
| imgPh | `#F2F0F0` | Ô ảnh khi chưa có ảnh | — |
| text | `#141414` | Chữ chính | `--foreground` |
| muted | `#6B6B6B` | Chữ phụ | `--muted-foreground` |
| faint | `#9E9A9B` | Placeholder, chú thích API | — |
| border | `#F0E6E8` | Viền nhạt, đường kẻ bảng | `--border` |
| borderStrong | `#DCCFD2` | Viền input, nút outline | `--input` |
| success / successSoft | `#2E7D4F` / `#E4F2E9` | Thông báo thành công, "Hoàn tất" | — |
| warning / warningSoft | `#A86A12` / `#FBF1DE` | "Đang xử lý", nhãn "Minh họa" | — |
| danger / dangerSoft | `#B42318` / `#FDE8E6` | Lỗi, nút xóa | `--destructive` = `#B42318` |
| info / infoSoft | `#3B5BA9` / `#E5EAF6` | "Đang giao", "Đang chạy" | — |

**Gradient (chỉ dùng ở các chỗ ghi rõ):**
- Hero trang chủ: `linear-gradient(90deg, #E8112D, #FF7A3D)` + 2 hình tròn trắng mờ (opacity 0.12–0.16) góc phải.
- Section "Gợi ý dành cho bạn": `linear-gradient(90deg, #FFE8EC, #FFF5EB)`.
- Ô icon thẻ thống kê / thanh biểu đồ: xoay vòng các cặp sáng
  `#FF7A3D→#FFC93C`, `#FF5E7E→#FFB38A`, `#FFA62B→#FFE36E`, `#FF7EB3→#FF9F5A`, `#FFB38A→#FFE066`, `#E8112D→#FF7EB3`.
- Không dùng màu xanh dương / tím của repo cũ (`blue-600`, `purple-600`, `indigo`).

### Chữ
- Font: **Inter**. Tiêu đề trang dùng **Inter Black (900)**, tiêu đề card dùng Bold (700).
- Cỡ: H1 trang 30px · hero 52px · tiêu đề section 24px · tiêu đề card 18–20px · body 14–15px · chú thích 12–13px.
- Logo "HUB": Inter Black 26px, màu `#E8112D`.

### Kích thước & hiệu ứng
- Container nội dung: rộng 1280px, padding ngang 80px (Tailwind: `max-w-[1280px] mx-auto px-4 lg:px-0`).
- Bo góc: card 10px · input/nút 8px · badge/pill 999px.
- Đổ bóng card: `0 1px 4px rgba(0,0,0,.07)`.
- Icon: **lucide-react** (repo đã có), stroke 2, cỡ 16–24.

---

## 2. Thành phần dùng chung

| Thành phần | Mô tả | File repo |
|---|---|---|
| **Header** | Nền trắng, viền dưới `border`. Trái: logo HUB · menu. Giữa: ô tìm kiếm (icon search, placeholder "Tìm kiếm sản phẩm...", chiếm phần còn lại). Phải: icon user + username · icon giỏ có badge đỏ số lượng. Link active: chữ đỏ Semi Bold. | `Header.tsx` |
| Menu theo role | **Buyer:** Trang chủ · Sản phẩm · Wishlist · Đơn hàng. **Admin:** thêm Admin · Dashboard. **Data Scientist:** Trang chủ · Sản phẩm · Data Science · Model · Lịch chạy · Phân tích lỗi. | `Header.tsx` |
| **ProductCard** | Ảnh vuông (placeholder nền `imgPh` + icon ảnh khi lỗi) · loại sản phẩm (12px muted) · tên (15px Semi Bold) · 5 sao + `(số đánh giá)` · giá đỏ 18px Bold · hàng nút: **[🛒 Giỏ]** đỏ (giãn hết chỗ) + **[👁]** outline + **[♥]** outline đỏ. Tùy chọn: badge điểm góc trái ảnh `#1 · 0.874` (nền đỏ, chữ trắng) — chỉ ở khối gợi ý. Bỏ badge "-x%". | `ProductCard.tsx` |
| Button | primary (nền đỏ, chữ trắng) · outline (trắng, viền borderStrong) · outlineRed (chữ/icon đỏ) · white (nền trắng chữ đỏ, dùng trên hero) · danger. Padding 10×18, bo 8. | `ui/button.tsx` |
| Badge trạng thái | pill nhạt + chữ đậm cùng tông: success / warning / info / danger / neutral. | `ui/badge.tsx` |
| Thông báo | Thành công: nền successSoft chữ success. Lỗi: nền dangerSoft viền danger + icon alert. | `ui/alert.tsx` |
| Empty state | Card trắng viền **nét đứt** borderStrong, icon 40px faint, tiêu đề 17px, mô tả 13px muted, căn giữa. | dùng trong các page |
| Chú thích API | Dòng 12px màu faint dưới mỗi màn (chỉ có trong Figma để đối chiếu, **không** render trong app). | — |

---

## 3. Luồng điều hướng (theo sơ đồ)

```
Đăng nhập ─(chưa có TK)→ Đăng ký → Đăng nhập
   │ POST /auth/login → {token, role_id}
   ├─ Buyer  → Trang chủ → Sản phẩm (tìm/lọc) → Chi tiết → (Giỏ drawer) → Thanh toán → Lịch sử đơn → Đánh giá
   │                     ↘ Gợi ý dành cho bạn (đọc Recommendations)        ↘ Wishlist
   ├─ Admin  → Admin CRUD (Users | Products | Orders) · Dashboard quản trị
   └─ Data Scientist → Data Science (EDA, Train AI) → Model metrics → Lịch chạy & huấn luyện → Phân tích lỗi
```

**Role id (giữ như repo):** 1 Seller (không dùng) · 2 Buyer · 3 Admin · 4 Data Scientist.
⚠️ Repo hiện bọc `/data-science` trong `AdminRoute` (chỉ role 3). Cần tạo `DataScientistRoute` cho role 4 (Admin vẫn được vào nếu muốn).

---

## 4. Đặc tả từng màn hình

> Cột "Node" để lấy ảnh/chi tiết qua Figma MCP. Đường dẫn route lấy theo `App.tsx`; route mới ghi **(mới)**.

### Buyer

| # | Màn | Node | Route | Component |
|---|---|---|---|---|
| 01 | Đăng nhập | `43:3` | `/login` | `LoginPage.tsx` |
| 02 | Đăng ký | `43:46` | `/register` | `RegisterPage.tsx` |
| 03 | Trang chủ | `43:86` | `/` | `HomePage.tsx`, `RecommendedProducts.tsx` |
| 04 | Sản phẩm (tìm kiếm & lọc) | `44:2` | `/products` | `ProductsPage.tsx` |
| 05 | Chi tiết sản phẩm | `44:396` | `/products/:id` | `ProductDetailPage.tsx` |
| 06 | Wishlist | `44:540` | `/wishlist` | `WishlistPage.tsx` |
| 07 | Giỏ hàng (drawer) | `45:2` | (overlay) | `CartSidebar.tsx` |
| 08 | Thanh toán | `45:248` | `/checkout` | `CheckoutPage.tsx` |
| 09 | Lịch sử đơn hàng | `45:378` | `/orders` | `OrdersPage.tsx` |
| 10 | Trạng thái rỗng & lỗi | `45:456` | — | dùng chung |

**01 · Đăng nhập** — Nền gradient hồng nhạt (`#FFF3F5 → #FFE3E8`), logo HUB 40px trên card. Card trắng 448px:
"Đăng Nhập" (26px Bold) · mô tả "Chọn loại đăng nhập trước khi vào hệ thống" · **segmented control 3 lựa chọn: Buyer / Admin / Data Scientist** (icon user / shield-check / brain; mục chọn nền trắng chữ đỏ) · alert lỗi (khi sai) · input "Tên Đăng Nhập", "Mật Khẩu" · nút đỏ full-width "Đăng Nhập {role}" · "Chưa có tài khoản? **Đăng ký ngay**".
Logic: sau login, nếu role chọn không khớp `role_id` → báo lỗi "Tài khoản này không có quyền …". Điều hướng: Buyer → `/`, Admin → `/admin`, DS → `/data-science`.

**02 · Đăng ký** — cùng nền & card. Trường: Tên Đăng Nhập, Email, Mật Khẩu, Xác Nhận Mật Khẩu, hàng 2 cột Giới Tính (select) + Tuổi. Nút "Đăng Ký", link "Đã có tài khoản? Đăng nhập". Thay `alert()` bằng alert trong card.

**03 · Trang chủ** — thứ tự section:
1. **Hero** cao 400px, gradient đỏ→cam, tiêu đề "Thời trang gợi ý cho bạn" (52px Black trắng), mô tả "Khám phá sản phẩm được chọn riêng từ lịch sử mua sắm của bạn", nút trắng chữ đỏ "Khám phá ngay" → `/products`.
2. **4 ô tính năng** (card trắng, icon đỏ 36px): Giao hàng nhanh · Sản phẩm chọn lọc · Cập nhật mỗi ngày ("Gợi ý được tính lại lúc 02:00") · Gợi ý cá nhân.
3. **Danh mục nổi bật** — 5 ô theo `index_group_name` H&M: **Ladieswear, Menswear, Baby/Children, Sport, Divided** (ảnh vuông bo 10 + tên). Click → `/products?index_group=…`.
4. **Bán chạy tuần này** (nền accentSoft, icon zap): 5 ProductCard. *(thay khối "Sản phẩm giảm giá" + đồng hồ đếm ngược của repo — bỏ hẳn)*
5. **Gợi ý dành cho bạn** (nền gradient hồng→kem, icon sparkles): 5 ProductCard **có badge điểm** `#rank · score`. Mô tả "Dựa trên sở thích và lịch sử mua hàng của bạn · Random Forest xếp hạng". Dữ liệu từ `apiService.getRecommendations(user.id, n)`. Nếu rỗng (cold start) → hiển thị bán chạy và đổi mô tả thành "Bạn chưa có lịch sử mua — đang hiển thị sản phẩm bán chạy".
6. **Sản phẩm mới**: 4 ProductCard (cột rộng 302px).
Mỗi header section: tiêu đề 24px Black bên trái, "Xem tất cả ›" đỏ bên phải.

**04 · Sản phẩm** — Tiêu đề "Tất cả sản phẩm" + "N sản phẩm thời trang". **Thanh lọc** (card trắng, 1 hàng): Tìm kiếm (icon search) · Danh mục (`index_group_name`) · Nhóm sản phẩm (`product_group_name`) · Màu sắc (`colour_group_name`) · Sắp xếp (Bán chạy tuần / Giá tăng / Giá giảm / Mới nhất) · nút đỏ "Lọc". Dưới đó: chip các bộ lọc đang bật (nền accentSoft, có ×). Lưới 4 cột ProductCard. Phân trang (trang hiện tại nền đỏ).
API: `GET /product/search?name=…&attr=…` — **cần thêm** `apiService.searchProducts(params)` nếu chưa có; tạm thời có thể lọc phía client từ `getProducts`.

**05 · Chi tiết sản phẩm** — 2 cột: trái card ảnh 592×592; phải: breadcrumb `Danh mục / Loại` · tên 34px Black · sao + "4.5 (8 đánh giá)" · giá 34px Black đỏ + "giá tham khảo (đã chuẩn hóa)" · **4 ô thông tin** 2×2: Màu, Loại, Nhóm, Họa tiết · mô tả (`detail_desc`) · nút "Thêm vào giỏ" (đỏ) + "Yêu thích" (outline đỏ) · thông báo thành công xanh "Đã thêm vào Wishlist".
Dưới: card **"Đánh giá sản phẩm"** (icon message): select số sao + nút "Gửi đánh giá"; danh sách review (sao, thời gian bên phải, "User: …"). Map trường: thay `base_colour/season/gender/quantity_in_stock` bằng `colour_group_name / product_type_name / product_group_name / graphical_appearance_name` (nếu backend chưa có thì hiển thị trường cũ tương đương, ghi TODO).

**06 · Wishlist** — "Wishlist" + "Các sản phẩm bạn đã đánh dấu yêu thích". Lưới 4 cột ProductCard, nút ♥ ở trạng thái đã thích (nền accentSoft) + icon ♥ đặc góc phải ảnh. Bấm ♥ lần nữa → `removeWishlistItem`.

**07 · Giỏ hàng (drawer)** — Overlay đen 50%. Drawer phải rộng 448px: header "Giỏ hàng (n)" + nút X · item (nền subtle, ảnh 80px, tên, giá đỏ, − số lượng +, icon thùng rác đỏ bên phải) · footer: Tạm tính · Phí vận chuyển "Miễn phí" (xanh) · **Tổng cộng** (20px Bold, số đỏ) · nút đỏ "Thanh toán".

**08 · Thanh toán** — 2 cột (832 + 416). Trái: card "Thông tin giao hàng" (icon pin đỏ): Họ và tên*, SĐT*/Email, Địa chỉ*, Tỉnh/Thành*/Quận/Huyện* (select), Ghi chú (textarea). Card "Phương thức thanh toán" (icon card): 2 option COD / Chuyển khoản — option chọn có viền đỏ + nền accentSoft + radio đỏ. Phải: card "Đơn hàng (n sản phẩm)" (thumbnail có badge số lượng), Tạm tính, Phí ship, Tổng cộng, nút "Đặt hàng". Thay `alert()` bằng toast (`sonner` đã có).

**09 · Lịch sử đơn hàng** — Mỗi đơn 1 card: "Đơn #xxxxxxxx" + ngày giờ | tổng tiền đỏ + **badge trạng thái** (Đang xử lý = warning, Đang giao = info, Hoàn tất = success, Đã hủy = danger) + nút outline đỏ **"Đánh giá"** (chỉ khi Hoàn tất). Dưới là các dòng "Tên x SL …… giá", phân cách bằng đường kẻ.
"Đánh giá" → mở dialog chọn sao + nhận xét → `POST /order/evaluate` (**cần thêm** `apiService.evaluateOrder` nếu chưa có). Đây là bước **Feedback** trong sơ đồ.

**10 · Trạng thái rỗng & lỗi** — banner lỗi API "Không kết nối được API sản phẩm: …" + 6 empty state: Chưa có sản phẩm · Wishlist trống · Chưa có đơn hàng · Giỏ hàng trống · **Chưa có lịch sử mua (cold start)** · Không có quyền truy cập. Dùng đúng câu chữ này trong các page tương ứng.

### Admin (role 3)

| # | Màn | Node | Route | Component |
|---|---|---|---|---|
| 11 | Admin · Người dùng | `46:3` | `/admin` (tab Users) | `AdminPage.tsx` |
| 12 | Admin · Sản phẩm | `46:166` | `/admin` (tab Products) | `AdminPage.tsx` |
| 13 | Admin · Đơn hàng | `46:367` | `/admin` (tab Orders) | `AdminPage.tsx` |
| 14 | Dashboard quản trị | `46:483` | `/dashboard` | `Dashboard.tsx` |

**Chung cho 11–13:** tiêu đề "Admin CRUD" + "Quản lý user, sản phẩm và đơn hàng", nút outline "Tải lại" (icon refresh). Banner thành công khi thao tác xong. **Tabs** dạng segmented (nền border, tab active nền trắng chữ đỏ + icon): Users · Products · Orders.

**11 · Users** — nút đỏ "+ Thêm user" bên phải tabs. Bảng: Username · Email · Role (select: **Buyer / Admin / Data Scientist** — bỏ Seller) · customer_id liên kết · Action (icon thùng rác đỏ).

**12 · Products** — 2 cột: form "Thêm sản phẩm" (360px) với các ô: article_id, prod_name, product_type_name, product_group_name, colour_group_name, index_group_name, price, image_url + nút Lưu / Reset. Bảng: Tên (thumbnail 36px + tên) · Loại · Giá TB · Danh mục · Action (nút "Sửa" outline, "Xóa" chữ đỏ).
*(Nếu backend vẫn dùng schema cũ thì giữ field cũ nhưng đổi nhãn hiển thị; ghi TODO.)*

**13 · Orders** — bên phải tabs: 2 ô lọc `time_period`, `category`. Mỗi đơn 1 card: "Đơn #…" + "User: customer_id" | tổng đỏ + select trạng thái (Pending / Delivering / Completed / Cancelled). Danh sách sản phẩm trong đơn.

**14 · Dashboard quản trị** — "Dashboard Quản Trị". Lưới 3×2 thẻ: ô icon 48px **gradient sáng** (xem mục 1) + nhãn + giá trị 28px Black: Doanh thu · Đơn hàng · Người dùng · Sản phẩm · Wishlist · Feedback. Card "Top sản phẩm": số thứ tự trong vòng tròn accentSoft chữ đỏ, tên, "Đã bán: n", doanh thu xanh bên phải. Nguồn `getDashboardMetrics()`; thiếu số → `—`.

### Data Scientist (role 4)

| # | Màn | Node | Route | Component |
|---|---|---|---|---|
| 15 | EDA & tiền xử lý | `47:3` | `/data-science` | `DataScientistPage.tsx` |
| 16 | Model metrics | `47:146` | `/data-science/model` **(mới)** | `ModelMetricsPage.tsx` **(mới)** |
| 17 | Lịch chạy & huấn luyện | `47:320` | `/data-science/schedule` **(mới)** | `TrainingSchedulePage.tsx` **(mới)** |
| 18 | Phân tích lỗi | `47:463` | `/data-science/errors` **(mới)** | `ErrorAnalysisPage.tsx` **(mới)** |

**Chung:** đầu trang = icon đỏ 32px + tiêu đề 30px Black + mô tả + nút bên phải. Header dùng menu DS (mục 2).

**15 · Data Science & Analytics** — nút đỏ "▶ Train AI" (`triggerAITraining`). Banner xanh khi kích hoạt. 2 cột card **Original · dữ liệu gốc** và **Normalized · sau tiền xử lý**, mỗi card là danh sách figure (caption trắng + ảnh báo cáo PNG) — giữ cơ chế import ảnh từ `data_scientist/reports/...` như repo, chỉ đổi style. Dưới: 2 card insight (icon trend / target) — **xóa nội dung bịa** ("Sản phẩm Apple…", "Giảm 45%…"), thay bằng "Điền sau khi chạy EDA trên dữ liệu H&M thật." hoặc đọc từ API.

**16 · Model metrics** — badge info "run_xxx · thời gian" + nút "Tải lại". Hàng 5 thẻ KPI (ô icon gradient): MAP@12 · Recall@12 · Precision@12 · NDCG@12 · Recall ứng viên. Hai card:
- "Random Forest so với baseline" (badge warning "Minh họa · chưa có số thật" khi chưa có data): 2 nhóm MAP@12, Recall@12; mỗi nhóm 3 thanh ngang — Random Forest (gradient cam→vàng), BL1 Top-12 bán chạy (hồng→cam), BL2 Mua lại gần nhất (xám `#DCCFD2`).
- "Chia dữ liệu theo thời gian": thanh 3 khúc Train (nền `#FFE3D3` chữ `#C2410C`) · Val (`#FFF3C4`/`#A16207`) · Test (`#FFE3E8`/`#E8112D`) + 3 dòng giải thích + "Mọi feature chỉ tính từ dữ liệu trước cutoff (chống rò rỉ)."
Card "Lịch sử lần chạy": bảng run_id · Thời gian · Subset · n_estimators · max_depth · MAP@12 (val) · Trạng thái (badge: Đã ghi Recommendations / Kém hơn baseline / Lỗi dữ liệu).
API: `GET /dashboard/metrics` — **cần thêm** hàm/endpoint metrics model nếu backend chưa có; frontend phải chịu được thiếu dữ liệu.

**17 · Lịch chạy & huấn luyện** — nút "Lưu cấu hình" (outline) + "Train AI" (đỏ). Trái: card "Lịch tự động" (toggle đỏ "Chạy mỗi ngày lúc 02:00", 3 ô: Giờ chạy, Lần chạy kế tiếp, Top n) · card "Cấu hình Random Forest" (Số tuần dữ liệu, Số ứng viên/khách, Tỉ lệ dương:âm, n_estimators, max_depth, min_samples_leaf). Phải: card "Tiến trình · run_xxx" (badge Đang chạy) với 6 bước có vòng tròn trạng thái (xong = xanh ✓, đang chạy = đỏ, chờ = xám) + thanh tiến độ gradient · card "Ngoại lệ" (alert warning "Metrics kém hơn baseline", alert danger "Dữ liệu lỗi", nút "Vẫn ghi đè" danger + "Giữ bản cũ" outline).
6 bước: Chọn subset & chia theo thời gian → Sinh ứng viên → Tạo feature → Huấn luyện Random Forest → Đánh giá vs baseline → Ghi bảng Recommendations.

**18 · Phân tích lỗi** — nút "Xuất CSV". 2 card bảng: "Theo nhóm khách" (cold start / 1–2 / 3–10 / >10 giao dịch × Số khách, MAP@12, Recall@12) và "Theo nhóm sản phẩm" (`product_group_name` × Số món mua, Precision@12, Recall@12). 2 card biểu đồ thanh: "Feature importance (Random Forest)" (8 feature, thanh gradient xoay vòng) và "Ứng viên bị bỏ sót" (recall theo nguồn: Mua lại, Bán chạy tuần, Cùng product_code, Co-purchase, Tất cả nguồn) + ô "Điều chỉnh Top n" + nút "Áp dụng & tính lại" (khối **Adjust n** trong sơ đồ).

---

## 5. Thứ tự làm đề xuất

1. `theme.css` + font Inter → token màu mục 1. Thay toàn bộ class `blue-*`, `purple-*`, `indigo-*` sang token mới.
2. `Header.tsx` (logo HUB, menu theo role, badge giỏ) + `ProductCard.tsx`.
3. Login/Register (segmented 3 role, sửa điều hướng) + `DataScientistRoute`.
4. Buyer: Home → Products (lọc) → Detail → Wishlist → Cart → Checkout → Orders (+ dialog đánh giá) → empty states.
5. Admin: AdminPage (tabs, bỏ Seller) → Dashboard.
6. Data Scientist: restyle `DataScientistPage` → tạo 3 page mới + route.
7. Chạy `npm run build` để chắc không lỗi type; chụp lại từng màn so với Figma.

## 6. Checklist nghiệm thu

- [ ] Không còn chữ "ShopVN", không còn màu xanh/tím cũ.
- [ ] Không có số liệu bịa; thiếu dữ liệu hiển thị `—`.
- [ ] Không hiện `₫` và % giảm giá; giá là số chuẩn hóa.
- [ ] Role chọn khi login khớp `role_id`; DS vào được `/data-science/*`, Buyer không vào được trang Admin/DS.
- [ ] Khối "Gợi ý dành cho bạn" lấy từ API recommendation, có badge điểm, có fallback cold start.
- [ ] Có bước Feedback sau mua (nút "Đánh giá" ở đơn Hoàn tất).
- [ ] Các empty state / lỗi dùng đúng câu chữ ở màn 10.
- [ ] `npm run build` chạy qua.
