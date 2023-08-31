from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .auth import get_current_user
from models import SellProduct, WishlistItem
from database import SessionLocal

wishlist_router = APIRouter(
    prefix="/wishlist",
    tags=["wishlist"],
    responses={401: {"detail": "Not authorized"}}
)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add a product to the wishlist
@wishlist_router.post("/add_product/{product_id}")
def add_product_to_wishlist(product_id: int,
                            user: dict = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    product = db.query(SellProduct).filter(SellProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    existing_wishlist_item = db.query(WishlistItem).filter(
        WishlistItem.user_id == user.get("user_id"),
        WishlistItem.product_id == product_id
    ).first()

    if existing_wishlist_item:
        raise HTTPException(status_code=400, detail="Product already in wishlist")
    wishlist_item = WishlistItem(
        user_id=user.get("user_id"),
        product_id=product_id
    )
    db.add(wishlist_item)
    db.commit()
    return {"message": "Product added to wishlist"}

# Get all products in the wishlist
@wishlist_router.get("/get_products")
def get_products_in_wishlist(user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    wishlist_items = db.query(WishlistItem).filter(WishlistItem.user_id == user.get("user_id")).all()
    products = []

    for wishlist_item in wishlist_items:
        product = db.query(SellProduct).filter(SellProduct.id == wishlist_item.product_id).first()
        if product:
            products.append({
                "product_id": product.id,
                "product_name": product.title,
                "product_price": product.price
            })

    return products

# Delete items from the wishlist
@wishlist_router.delete("/delete_product/{product_id}")
def delete_product_from_wishlist(product_id: int,
                                 user: dict = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    wishlist_item = db.query(WishlistItem).filter(
        WishlistItem.user_id == user.get("user_id"),
        WishlistItem.product_id == product_id
    ).first()

    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Product not found in wishlist")

    db.delete(wishlist_item)
    db.commit()
    return {"message": "Product deleted from wishlist"}
