from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db

# Pipeline GNN cũ (dataset Myntra). /trigger-training đã chuyển sang pipeline H&M ở routers/hm_ai.py.
# Import trễ để backend khởi động không phải nạp torch/torchvision.

router = APIRouter()


@router.get("/reports/original/latest")
async def get_latest_original_report(db: Session = Depends(get_db)):
    """
    API lấy báo cáo EDA dữ liệu gốc (Original) của phiên bản mới nhất.
    """
    from services.model_ai_service import AIPipelineService
    service = AIPipelineService(db)
    data, error = await service.get_latest_eda_report_service("original")

    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    return data


@router.get("/reports/normalized/latest")
async def get_latest_normalized_report(db: Session = Depends(get_db)):
    """
    API lấy báo cáo EDA dữ liệu chuẩn hóa (Normalized) của phiên bản mới nhất.
    """
    from services.model_ai_service import AIPipelineService
    service = AIPipelineService(db)
    data, error = await service.get_latest_eda_report_service("normalized")

    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    return data
