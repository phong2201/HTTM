from sqlalchemy.orm import Session
from models.product_model import Product
from schemas.product_schema import ProductCreate, ProductUpdate
from uuid import UUID

def create_product(db: Session, product_in: ProductCreate):
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_id(db: Session, product_id: UUID):
    return db.query(Product).filter(Product.id == product_id).first()

def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    # Sản phẩm bị ẩn (vd dataset cũ sau khi nạp H&M) không hiện trong danh sách
    return db.query(Product).filter(Product.is_active.is_(True)).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: UUID, product_in: ProductUpdate):
    """Cập nhật sản phẩm (PUT)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    
    if not db_product:
        return None
    
    # Chỉ update những field được pass
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product_quantity(db: Session, product_id: UUID, quantity: int):
    """Cập nhật số lượng trong kho (PATCH)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    
    if not db_product:
        return None
    
    db_product.quantity_in_stock = quantity
    db.commit()
    db.refresh(db_product)
    return db_product