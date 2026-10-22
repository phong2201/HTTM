from sqlalchemy.orm import Session
from models.wishlist_model import Wishlist
from models.product_model import Product
from models.user_model import User
from models.cart_model import Cart
from uuid import UUID

def add_product_to_cart(db: Session, user_id: UUID, product_id: UUID, request_quantity: int) -> Cart:    
    cart_item = Cart(
        user_id=user_id, 
        product_id=product_id, 
        quantity=request_quantity)
    
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item

def add_product_to_cart_no_commit(db: Session, user_id: UUID, product_id: UUID, request_quantity: int) -> Cart:    
    cart_item = check_product_in_cart(db, user_id, product_id)
    if cart_item:
        cart_item.quantity += request_quantity
    else:
        cart_item = Cart(
            user_id=user_id, 
            product_id=product_id, 
            quantity=request_quantity)
        db.add(cart_item)
    
    db.flush()  # Flush to DB session nhưng không commit
    
    return cart_item
    
def check_product_in_cart(db: Session, user_id: UUID, product_id: UUID) -> Cart:
    return db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == product_id
    ).first()

def check_product_exists(db: Session, product_id: UUID) -> Product:
    return db.query(Product).filter(
        Product.id == product_id
    ).first()

def get_user_cart(db: Session, user_id: UUID):
    return db.query(Cart).filter(Cart.user_id == user_id).all()

def update_cart_quantity(db: Session, user_id: UUID, product_id: UUID, quantity: int):
    cart_item = check_product_in_cart(db, user_id, product_id)
    if not cart_item:
        return None
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_cart_item(db: Session, user_id: UUID, product_id: UUID) -> bool:
    cart_item = check_product_in_cart(db, user_id, product_id)
    if not cart_item:
        return False
    db.delete(cart_item)
    db.commit()
    return True

def clear_user_cart(db: Session, user_id: UUID):
    db.query(Cart).filter(Cart.user_id == user_id).delete()
    db.commit()
