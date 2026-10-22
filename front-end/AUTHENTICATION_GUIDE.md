# 🎉 Hệ Thống Xác Thực (Authentication) - Hướng Dẫn

## ✅ Những Gì Đã Được Tích Hợp

### 1️⃣ **Login & Register Pages**
- ✨ Trang đăng nhập (`/login`) với giao diện đẹp
- ✨ Trang đăng ký (`/register`) với validation đầy đủ
- ✨ Cả hai trang đều hỗ trợ tiếng Việt

### 2️⃣ **API Service** (`src/services/api.ts`)
Đã tạo class `APIService` tích hợp với backend tại `http://localhost:8080`

**Các endpoints chính:**
- `POST /auth/login` - Đăng nhập
- `POST /auth/register` - Đăng ký tài khoản
- `GET /products` - Lấy danh sách sản phẩm
- `POST /cart/add` - Thêm vào giỏ hàng
- `POST /wishlist/add` - Thêm vào wishlist
- `GET /recommendations` - Lấy sản phẩm đề xuất

### 3️⃣ **Authentication Context** (`src/context/AuthContext.tsx`)
- 🔐 Quản lý trạng thái đăng nhập toàn ứng dụng
- 💾 Lưu token JWT vào localStorage
- 🎣 Hook `useAuth()` dễ sử dụng

### 4️⃣ **Protected Routes** (`src/app/components/ProtectedRoute.tsx`)
- Tất cả các route chính (/, /products, /dashboard, etc.) đã được bảo vệ
- Nếu chưa đăng nhập, sẽ tự động chuyển hướng tới `/login`

### 5️⃣ **Header với Auth UI**
- Hiển thị tên người dùng sau khi đăng nhập
- Nút đăng xuất (logout)
- Dropdown menu với thông tin tài khoản

## 🚀 Cách Sử Dụng

### Chạy Development Server
```bash
npm run dev
# Ứng dụng sẽ chạy tại http://localhost:5173
```

### Chạy Backend (Nếu chưa chạy)
```bash
cd api/intelligent-system/backend

# Tạo virtual environment (nếu chưa có)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  (Windows)

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy backend
python main.py
# Backend sẽ chạy tại http://localhost:8080
```

## 🧪 Hướng Dẫn Test

### 1. Đăng Ký Tài Khoản Mới
1. Truy cập http://localhost:5173/register
2. Điền vào form:
   - Tên đăng nhập: `testuser`
   - Email: `test@example.com`
   - Mật khẩu: `password123`
   - Xác nhận mật khẩu
   - (Tùy chọn) Giới tính, Tuổi
3. Nhấn "Đăng Ký"

### 2. Đăng Nhập
1. Chuyển tới http://localhost:5173/login
2. Điền:
   - Tên đăng nhập: `testuser`
   - Mật khẩu: `password123`
3. Nhấn "Đăng Nhập"
4. Bạn sẽ được chuyển hướng tới trang chủ

### 3. Kiểm Tra Trạng Thái
- Xem tên người dùng ở header (góc phải)
- Nhấp vào để xem dropdown menu
- Nhấn "Đăng xuất" để đăng xuất

## 🔧 Cách Lấy Token & Gọi API

### Trong React Component
```tsx
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/services/api';

function MyComponent() {
  const { isAuthenticated, user } = useAuth();

  // Gọi API
  const fetchData = async () => {
    try {
      const products = await apiService.getProducts();
      console.log(products);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      {isAuthenticated && <p>Xin chào, {user?.username}!</p>}
      <button onClick={fetchData}>Tải Sản Phẩm</button>
    </div>
  );
}
```

## 📝 Cấu Trúc File

```
src/
├── services/
│   └── api.ts                 # API client & config
├── context/
│   └── AuthContext.tsx        # Auth state & logic
└── app/components/
    ├── Header.tsx             # Header với auth UI
    ├── LoginPage.tsx          # Trang đăng nhập
    ├── RegisterPage.tsx       # Trang đăng ký
    └── ProtectedRoute.tsx     # Bảo vệ routes
```

## 🔐 Token Management

Token được tự động:
- ✅ Lưu vào `localStorage` sau khi đăng nhập
- ✅ Đính kèm vào header `Authorization: Bearer <token>` cho mỗi request
- ✅ Xóa khi người dùng đăng xuất

## 🎯 Tiếp Theo (Optional)

### Để enhance thêm:
1. **Refresh Token**: Thêm endpoint refresh token từ backend
2. **User Profile**: Tạo trang profile để edit thông tin
3. **Password Reset**: Thêm forgot password functionality
4. **Social Login**: Tích hợp OAuth (Google, Facebook)
5. **2FA**: Thêm Two-Factor Authentication

## ⚠️ Lưu Ý Quan Trọng

1. **CORS**: Backend phải allow origins từ frontend (đã cấu hình cho `*`)
2. **Token Expiry**: Kiểm tra backend để biết token hết hạn khi nào
3. **API URL**: Đảm bảo backend chạy tại `http://localhost:8080`
4. **Mật khẩu**: Luôn sử dụng HTTPS trên production

## ❓ Câu Hỏi Thường Gặp

**Q: Làm sao để tùy chỉnh token expiry?**
A: Kiểm tra `backend/services/auth_service.py` để cấu hình

**Q: Sao không thể đăng nhập?**
A: Kiểm tra:
- Backend đang chạy tại `http://localhost:8080`?
- Tài khoản có tồn tại trong cơ sở dữ liệu không?
- Mật khẩu có chính xác không?

**Q: Làm sao để log out từ tất cả devices?**
A: Thêm endpoint `/auth/logout` trong backend và gọi khi người dùng logout

Chúc bạn phát triển thành công! 🎊
