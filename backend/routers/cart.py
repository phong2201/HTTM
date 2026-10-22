from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.cart_schema import CartItemAdd, CartItemResponse
from schemas.base_schema import IMessageResponse
from dependencies.auth_deps import get_current_user
from models.cart_model import Cart
from models.product_model import Product
from models.user_model import User
from services import cart_service
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_product_to_cart(
    cart_in: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await cart_service.add_product_to_cart(current_user.id, cart_in.product_id, cart_in.quantity, db)

@router.get("", response_model=List[CartItemResponse])
async def get_my_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await cart_service.get_user_cart(current_user.id, db)

@router.patch("/{product_id}", response_model=CartItemResponse)
async def update_cart_item(
    product_id: UUID,
    cart_in: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await cart_service.update_cart_quantity(current_user.id, product_id, cart_in.quantity, db)

@router.delete("/{product_id}", response_model=IMessageResponse)
async def remove_cart_item(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await cart_service.remove_cart_item(current_user.id, product_id, db)
