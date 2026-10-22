# Intelligent Fashion Recommendation System

Ung dung thuong mai dien tu thoi trang tich hop he thong goi y san pham. Du an gom frontend React/Vite, backend FastAPI va cac script data science de xu ly du lieu, trich xuat dac trung va huan luyen mo hinh goi y.

## Chuc nang chinh

- Dang ky, dang nhap va quan ly phien bang JWT.
- Xem danh sach san pham, chi tiet san pham va san pham de xuat.
- Gio hang, wishlist, thanh toan va lich su don hang.
- Trang admin de quan ly san pham, nguoi dung, dashboard va du lieu.
- Backend REST API cho authentication, products, cart, wishlist, orders, recommendations va feedback.
- Pipeline data science cho tien xu ly du lieu thoi trang, feature extraction, graph building va training GNN.

## Cong nghe

- Frontend: React, TypeScript, Vite, React Router, Tailwind CSS, Radix UI, MUI icons.
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT, PostgreSQL.
- Data science: Python scripts cho EDA, preprocessing, feature fusion, graph data va prediction.
- Database: PostgreSQL qua `DATABASE_URL`.

## Cau truc thu muc

```text
.
├── src/                              # Frontend React/Vite
│   ├── app/components/               # Pages va UI components
│   ├── context/AuthContext.tsx       # Trang thai dang nhap
│   └── services/api.ts               # API client
├── api/intelligent-system/
│   ├── backend/                      # FastAPI backend
│   │   ├── routers/                  # API routes
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/                 # Business logic
│   │   └── main.py                   # Entry point backend
│   └── data_scientist/               # Dataset, EDA va ML pipeline
├── AUTHENTICATION_GUIDE.md           # Huong dan chi tiet ve xac thuc
├── test-api.sh                       # Script test nhanh API
└── package.json                      # Scripts va dependencies frontend
```

## Yeu cau moi truong

- Node.js 18+.
- npm.
- Python 3.10+.
- PostgreSQL 15+ hoac Docker/Docker Compose neu muon chay database bang container.

## Cai dat frontend

```bash
npm install
```

Tao file `.env` o thu muc goc neu can doi API URL:

```env
VITE_API_BASE_URL=http://localhost:8080
```

Chay frontend:

```bash
npm run dev
```

Mac dinh frontend chay tai:

```text
http://localhost:5173
```

Build production:

```bash
npm run build
```

## Cai dat backend

Di chuyen vao thu muc backend:

```bash
cd api/intelligent-system/backend
```

Tao va kich hoat virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Tren Windows:

```bash
venv\Scripts\activate
```

Cai dependencies:

```bash
pip install -r requirements.txt
```

Tao file `.env` trong `api/intelligent-system/backend`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5436/intelligent_system
SECRET_KEY=change-this-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=intelligent_system
```

Neu dung `docker-compose.yml` trong backend, cac bien `DB_USERNAME`, `DB_PASSWORD`, `DB_DATABASE` se duoc dung de tao PostgreSQL container.

Chay PostgreSQL bang Docker:

```bash
docker compose up -d db
```

Chay backend:

```bash
python main.py
```

Backend mac dinh chay tai:

```text
http://localhost:8080
```

Tai lieu API cua FastAPI:

```text
http://localhost:8080/docs
```

## Chay bang Docker Compose

Trong thu muc `api/intelligent-system/backend`, co the chay ca database va API:

```bash
docker compose up --build
```

Sau do chay frontend o thu muc goc:

```bash
npm run dev
```

## Tai khoan admin mac dinh

Backend tu dong tao/cap nhat admin khi khoi dong:

```text
username: quangkhaiadmin
password: 123456
```

Dung tai khoan nay de vao cac trang can quyen admin nhu `/admin`, `/dashboard` va `/data-science`.

## Routes frontend

- `/login`: Dang nhap.
- `/register`: Dang ky.
- `/`: Trang chu.
- `/products`: Danh sach san pham.
- `/products/:id`: Chi tiet san pham.
- `/wishlist`: Danh sach yeu thich.
- `/orders`: Don hang cua nguoi dung.
- `/checkout`: Thanh toan.
- `/admin`: Quan tri.
- `/dashboard`: Dashboard admin.
- `/data-science`: Trang data science cho admin.

## API endpoints chinh

- `POST /auth/register`: Dang ky.
- `POST /auth/login`: Dang nhap.
- `GET /users/me`: Lay thong tin nguoi dung hien tai.
- `GET /products`: Lay danh sach san pham.
- `GET /products/{id}`: Lay chi tiet san pham.
- `GET /cart`, `POST /cart`, `PATCH /cart/{product_id}`, `DELETE /cart/{product_id}`: Gio hang.
- `GET /wishlist`, `POST /wishlist`, `DELETE /wishlist/{product_id}`: Wishlist.
- `GET /orders/me`, `GET /orders`, `POST /orders`: Don hang.
- `GET /predict/{user_id}?k=10`: Goi y san pham cho nguoi dung.
- `GET /dashboard/metrics`: Du lieu dashboard admin.

## Test nhanh API

Can cai `curl` va `jq`, sau do chay backend truoc:

```bash
./test-api.sh
```

Script se test health check, dang ky, dang nhap, lay san pham va goi y.

## Data science pipeline

Thu muc `api/intelligent-system/data_scientist` chua cac script:

- `0_create_file_csv.py`: Tao file CSV dau vao.
- `eda_original_1.py`: EDA du lieu goc.
- `preprocessing_2.py`: Tien xu ly du lieu.
- `eda_normalized_3.py`: EDA du lieu da chuan hoa.
- `image_extractor_4_1.py`, `text_extractor_4_3.py`, `metadata_extractor_4_2.py`: Trich xuat dac trung.
- `feature_fusion_4_4.py`: Hop nhat dac trung.
- `edge_builder_4_5.py`: Tao graph edges.
- `train_GNN_4_6.py`: Huan luyen GNN.
- `5_predict.py`: Du doan/goi y.

Nen chay cac script theo thu tu tren de dam bao file trung gian duoc tao dung.

## Ghi chu

- Neu frontend bao loi ket noi API, kiem tra backend co chay tai `http://localhost:8080` va bien `VITE_API_BASE_URL` co dung khong.
- Neu backend loi `DATABASE_URL`, kiem tra file `.env` trong `api/intelligent-system/backend`.
- Huong dan chi tiet rieng ve authentication nam trong `AUTHENTICATION_GUIDE.md`.
