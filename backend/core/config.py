from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-commerce with Recommendation System"
    
    DATABASE_URL: str
    # cấu hình bảo mật 
    SECRET_KEY: str = "secret" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # token hết hạn sau 7 ngày 

    # URL công khai của backend — dùng để ghép link ảnh sản phẩm / báo cáo
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8000"

    # Pipeline H&M (data_scientist/hm_pipeline). Để trống = mặc định trong repo.
    HM_RUNS_DIR: str = ""          # mặc định: data_scientist/runs
    HM_DATA_DIR: str = ""          # mặc định: data/hm (chỉ cần khi chạy local)
    KAGGLE_KERNEL_SLUG: str = ""   # mặc định: <username trong kaggle.json>/hub-rf-pipeline
    # Giá H&M là giá đã chuẩn hóa (vd 0.0253). Quy đổi ước lượng sang VND: giá × hệ số, làm tròn nghìn.
    # 20.000.000 → trung vị ~506.000₫, 80% sản phẩm trong khoảng ~260.000–1.150.000₫.
    HM_PRICE_TO_VND: float = 20_000_000

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()