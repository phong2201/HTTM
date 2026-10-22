from sqlalchemy.orm import Session
from models.wishlist_model import Wishlist
from models.product_model import Product
from models.user_model import User
from uuid import UUID

def add_product_to_wishlist(db: Session, user_id: UUID, product_id: UUID) -> Wishlist:
    product = check_product_exists(db, product_id)
    if not product:
        return None
    
    existing = check_product_in_wishlist(db, user_id, product_id)
    
    if existing:
        return existing
    
    # Thêm vào wishlist
    wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)

    return wishlist_item

def get_user_wishlist(db: Session, user_id: UUID):
    return db.query(Wishlist).filter(Wishlist.user_id == user_id).all()

def remove_product_from_wishlist(db: Session, user_id: UUID, product_id: UUID) -> bool:
    wishlist_item = check_product_in_wishlist(db, user_id, product_id)
    
    if not wishlist_item:
        return False
    
    db.delete(wishlist_item)
    db.commit()

    return True

def check_product_in_wishlist(db: Session, user_id: UUID, product_id: UUID) -> Wishlist:
    return db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first() 

def check_product_exists(db: Session, product_id: UUID) -> Product:
    return db.query(Product).filter(
        Product.id == product_id
    ).first()
