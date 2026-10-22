from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import repositories.product_repository as product_repo
from schemas.product_schema import ProductCreate, ProductUpdate
from uuid import UUID
from models.interaction_model import Interaction, InteractionType

async def create_new_product(product_in: ProductCreate, db: Session):
    """Tạo sản phẩm mới"""
    return product_repo.create_product(db, product_in)

async def get_product_by_id(user_id: UUID, product_id: UUID, db: Session):
    product = product_repo.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )
    
    interaction = Interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=InteractionType.VIEWED)
    db.add(interaction)
    db.commit()

    return product

async def list_products_logic(skip: int, limit: int, db: Session):
    return product_repo.get_all_products(db, skip=skip, limit=limit)

async def update_product_logic(product_id: UUID, product_in: ProductUpdate, db: Session):
    product = product_repo.update_product(db, product_id, product_in)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )
    
    return product

async def update_product_quantity_logic(product_id: UUID, quantity: int, db: Session):
    """Cập nhật số lượng trong kho """
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Số lượng không thể là số âm"
        )
    
    product = product_repo.update_product_quantity(db, product_id, quantity)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )
    
    return product

async def delete_product_logic(product_id: UUID, db: Session):
    product = product_repo.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )

    db.delete(product)
    db.commit()
    return {"message": "Đã xóa sản phẩm"}
