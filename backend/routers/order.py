from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from database import get_db
from dependencies.auth_deps import get_current_user, require_admin
from models.user_model import User
from models.cart_model import Cart
from models.order_model import Order, OrderItem, OrderStatus
from models.product_model import Product
from schemas.order_schema import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not order_in.items:
        raise HTTPException(status_code=422, detail="Đơn hàng cần ít nhất một sản phẩm")

    order_items: list[OrderItem] = []
    total_amount = 0.0

    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Sản phẩm {item.product_id} không tồn tại")
        if not product.is_active:
            raise HTTPException(status_code=422, detail=f"Sản phẩm {product.prod_name} đã ngừng bán")
        if item.quantity < 1:
            raise HTTPException(status_code=422, detail="Số lượng phải lớn hơn 0")

        unit_price = product.price
        subtotal = unit_price * item.quantity
        total_amount += subtotal
        order_items.append(OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        ))

    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        note=order_in.note,
        status=OrderStatus.PENDING,
        items=order_items,
    )
    db.add(order)
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    db.commit()
    db.refresh(order)
    return order


@router.get("/me", response_model=list[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.user_id == current_user.id)
        .order_by(Order.order_date.desc())
        .all()
    )


@router.get("", response_model=list[OrderResponse])
async def get_all_orders(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .order_by(Order.order_date.desc())
        .limit(100)
        .all()
    )


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    status_value: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    try:
        order.status = OrderStatus(status_value)
    except ValueError:
        raise HTTPException(status_code=422, detail="Trạng thái đơn hàng không hợp lệ")
    db.commit()
    db.refresh(order)
    return order
