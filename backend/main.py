import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from database import engine, Base
from database import SessionLocal
from models.user_model import User, Role
from core.security import get_password_hash
# Import router
# from routers import model_ai  # Temporarily commented to avoid installing all ML dependencies
from routers import auth, product, wishlist, cart, order, dashboard, user, model_ai
from routers import recommendation
from routers import feedback
from routers import hm_ai
from models import hm_model, sales_model  # noqa: F401 — tạo bảng user_customer_links, sales_*
from services.hm_pipeline_service import pipeline
from services import sales_service

Base.metadata.create_all(bind=engine)


def ensure_default_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "kuroisme").first()
        if admin:
            admin.role_id = Role.ADMIN
            admin.password_hash = get_password_hash("123456")
        else:
            admin = User(
                username="kuroisme",
                email="kuroisme@example.com",
                password_hash=get_password_hash("123456"),
                role_id=Role.ADMIN,
            )
            db.add(admin)
        db.commit()
    finally:
        db.close()


ensure_default_admin()

@asynccontextmanager
async def lifespan(_: FastAPI):
    pipeline.start_scheduler()  # lịch chạy pipeline H&M (mặc định 02:00)
    sales_service.start_scheduler()  # tổng hợp doanh số theo ngày + chốt sổ tháng/năm
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Intelligent System API",
    description="Backend API cho hệ thống Recommendation",
    version="1.0.0"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = PROJECT_ROOT / "data_scientist" / "images"

if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(hm_ai.router)
app.include_router(model_ai.router, prefix="/ai", tags=["AI Pipeline (GNN cũ)"])
app.include_router(product.router, prefix="/products", tags=["Products"])
app.include_router(wishlist.router, prefix="/wishlist", tags=["Wishlist"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(order.router)
app.include_router(dashboard.router)
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(recommendation.router)
app.include_router(feedback.router)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Welcome to the Intelligent System API!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
