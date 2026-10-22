from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth_deps import require_admin
from models.cart_model import Cart
from models.feedback_model import Feedback
from models.order_model import Order, OrderItem
from models.product_model import Product
from models.user_model import User
from models.wishlist_model import Wishlist

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/sales")
async def get_sales_summary(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Doanh số hôm nay / tháng này / năm nay + các tháng, năm đã chốt sổ (services/sales_service.py)."""
    from services import sales_service
    return sales_service.summary(db)


@router.get("/metrics")
async def get_dashboard_metrics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product_count = db.query(func.count(Product.id)).scalar() or 0
    order_count = db.query(func.count(Order.id)).scalar() or 0
    user_count = db.query(func.count(User.id)).scalar() or 0
    revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
    cart_count = db.query(func.count(Cart.id)).scalar() or 0
    wishlist_count = db.query(func.count(Wishlist.id)).scalar() or 0
    feedback_count = db.query(func.count(Feedback.id)).scalar() or 0

    top_products = (
        db.query(
            Product.id,
            Product.prod_name,
            Product.image_url,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold"),
            func.coalesce(func.sum(OrderItem.subtotal), 0).label("revenue"),
        )
        .outerjoin(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.coalesce(func.sum(OrderItem.quantity), 0).desc(), Product.created_at.desc())
        .limit(8)
        .all()
    )

    return {
        "summary": {
            "products": product_count,
            "orders": order_count,
            "users": user_count,
            "revenue": revenue,
            "cart_items": cart_count,
            "wishlist_items": wishlist_count,
            "feedbacks": feedback_count,
        },
        "top_products": [
            {
                "id": str(item.id),
                "name": item.prod_name,
                "image_url": item.image_url,
                "sold": int(item.sold or 0),
                "revenue": float(item.revenue or 0),
            }
            for item in top_products
        ],
    }
