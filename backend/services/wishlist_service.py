from sqlalchemy.orm import Session
from uuid import UUID
from models.interaction_model import Interaction, InteractionType
import repositories.wishlist_repository as wishlist_repo

async def add_product_to_wishlist(user_id: UUID, product_id: UUID, db: Session):
    wishlist_item = wishlist_repo.add_product_to_wishlist(db, user_id, product_id)
    
    if not wishlist_item:
        return None
    
    interaction = Interaction(
        user_id=user_id, 
        product_id=product_id, 
        interaction_type=InteractionType.ADDED_TO_WISHLIST)
    db.add(interaction)
    db.commit()
    
    return wishlist_item

async def remove_product_from_wishlist_logic(user_id: UUID, product_id: UUID, db: Session):
    removed_wishlist_item = wishlist_repo.remove_product_from_wishlist(db, user_id, product_id)
    
    if not removed_wishlist_item:
        return None

    interaction = Interaction(
        user_id=user_id,
        product_id=product_id,
        interaction_type=InteractionType.REMOVED_FROM_WISHLIST
    )
    db.add(interaction)
    db.commit()
    
    return removed_wishlist_item

async def get_user_wishlist(user_id: UUID, db: Session):
    return wishlist_repo.get_user_wishlist(db, user_id)
