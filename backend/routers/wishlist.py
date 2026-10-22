from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.wishlist_schema import WishlistAdd, WishlistResponse
from schemas.base_schema import IMessageResponse
from dependencies.auth_deps import get_current_user
from models.user_model import User
from services import wishlist_service
from typing import List
from uuid import UUID

router = APIRouter()
@router.post("", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    wishlist_in: WishlistAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wishlist_item = await wishlist_service.add_product_to_wishlist(
        current_user.id,
        wishlist_in.product_id,
        db
    )
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sản phẩm không tồn tại"
        )
    
    return wishlist_item

@router.get("", response_model=List[WishlistResponse])
async def get_my_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wishlist_items = await wishlist_service.get_user_wishlist(
        current_user.id,
        db
    )
    return wishlist_items

@router.delete("/{product_id}", response_model=IMessageResponse)
async def remove_from_wishlist(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa sản phẩm khỏi wishlist"""
    result = await wishlist_service.remove_product_from_wishlist_logic(
        current_user.id,
        product_id,
        db
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sản phẩm không có trong wishlist"
        )
    
    return {"message": "Đã xóa khỏi wishlist"}