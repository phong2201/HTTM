from typing import Literal, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth_deps import require_admin, require_data_scientist
from models.hm_model import UserCustomerLink
from models.user_model import User
from services.hm_pipeline_service import pipeline

router = APIRouter(prefix="/ai", tags=["AI Pipeline · H&M"])


class TrainingConfigIn(BaseModel):
    schedule_enabled: Optional[bool] = None
    schedule_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    runner: Optional[Literal["kaggle", "local"]] = None
    subset: Optional[Literal["sample", "full"]] = None
    customer_frac: Optional[float] = Field(None, gt=0, le=1)
    top_n: Optional[int] = Field(None, ge=1, le=50)
    weeks: Optional[int] = Field(None, ge=1, le=52)
    train_weeks: Optional[int] = Field(None, ge=1, le=8)
    candidates_per_customer: Optional[int] = Field(None, ge=12, le=200)
    neg_pos_ratio: Optional[float] = Field(None, gt=0)
    n_estimators: Optional[int] = Field(None, ge=1, le=2000)
    max_depth: Optional[int] = Field(None, ge=1, le=100)
    min_samples_leaf: Optional[int] = Field(None, ge=1)


class ResolveIn(BaseModel):
    action: Literal["overwrite", "keep"]


class RecomputeIn(BaseModel):
    top_n: int = Field(ge=1, le=50)


@router.post("/trigger-training", status_code=202)
def trigger_training(_: User = Depends(require_data_scientist)):
    """Chạy pipeline H&M ngay (Kaggle hoặc local theo cấu hình)."""
    return pipeline.trigger(source="manual")


@router.get("/training/status")
def training_status(_: User = Depends(require_data_scientist)):
    return pipeline.status()


@router.put("/training/config")
def save_training_config(config: TrainingConfigIn, _: User = Depends(require_data_scientist)):
    return pipeline.save_config(config.model_dump(exclude_none=True))


@router.post("/training/resolve")
def resolve_training_exception(body: ResolveIn, _: User = Depends(require_data_scientist)):
    return pipeline.resolve(body.action)


@router.post("/runs/{run_id}/import")
def import_run(run_id: str, force: bool = False, _: User = Depends(require_data_scientist)):
    """Nạp tay một thư mục data_scientist/runs/<run_id> (vd tải output kernel từ giao diện Kaggle)."""
    return pipeline.import_run(run_id, force=force)


@router.get("/metrics/latest")
def model_metrics(_: User = Depends(require_data_scientist)):
    return pipeline.metrics()


@router.get("/error-analysis")
def error_analysis(_: User = Depends(require_data_scientist)):
    return pipeline.error_analysis()


@router.post("/recommendations/recompute")
def recompute_recommendations(body: RecomputeIn, _: User = Depends(require_data_scientist)):
    return pipeline.recompute(body.top_n)


@router.get("/insights")
def insights(_: User = Depends(require_data_scientist)):
    """Nhận xét "Xu hướng sản phẩm" / "Tối ưu hóa gợi ý" tính từ kết quả run."""
    return pipeline.insights()


@router.get("/reports/eda")
def eda_reports(_: User = Depends(require_data_scientist)):
    return pipeline.eda_reports()


@router.get("/reports/{run_id}/{group}/{name}")
def report_image(run_id: str, group: str, name: str):
    # Không yêu cầu token vì thẻ <img> không gửi được header Authorization.
    return FileResponse(pipeline.report_path(run_id, group, name), media_type="image/png")


@router.get("/customer-links")
def customer_links(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return {str(link.user_id): link.customer_id for link in db.query(UserCustomerLink)}
