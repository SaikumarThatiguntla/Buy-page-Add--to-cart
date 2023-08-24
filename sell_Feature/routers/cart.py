from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .auth import get_current_user
from models import SellCart, SellProduct,ProductRating
from database import SessionLocal
from fastapi import Query

cart_router = APIRouter(
    prefix="/cart",
    tags=["cart"],
    responses={401: {"detail": "Not authorized"}}
)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add a product to the cart
@cart_router.post("/add_product/{product_id}")
def add_product_to_cart(product_id: int, quantity: int = 1,
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    product = db.query(SellProduct).filter(SellProduct.s_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = SellCart(
        s_user_id=user.get("user_id"),
        s_product_id=product_id,
        s_quantity=quantity
    )
    db.add(cart_item)
    db.commit()
    return {"message": "Product added to cart"}

# Get all products in the cart
@cart_router.get("/get_products")
def get_products_in_cart(user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    cart_items = db.query(SellCart).filter(SellCart.s_user_id == user.get("user_id")).all()
    products = []

    for cart_item in cart_items:
        product = db.query(SellProduct).filter(SellProduct.s_id == cart_item.s_product_id).first()
        if product:
            products.append({
                "product_id": product.s_id,
                "product_name": product.s_name,
                "product_price": product.s_price,
                "quantity": cart_item.s_quantity
            })

    return products

# Delete items from the cart
@cart_router.delete("/delete_product/{product_id}")
def delete_product_from_cart(product_id: int,
                             user: dict = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    cart_item = db.query(SellCart).filter(
        SellCart.s_user_id == user.get("user_id"),
        SellCart.s_product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found in cart")

    db.delete(cart_item)
    db.commit()
    return {"message": "Product deleted from cart"}

# ...
# Give a rating to a product
@cart_router.post("/rate_product/{product_id}")
def rate_product(product_id: int, rating: int,
                 user: dict = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    product = db.query(SellProduct).filter(SellProduct.s_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating value. Please provide a value between 1 and 5.")

    existing_rating = db.query(ProductRating).filter(
        ProductRating.pr_user_id == user.get("user_id"),
        ProductRating.pr_product_id == product_id
    ).first()

    if existing_rating:
        existing_rating.pr_rating = rating
    else:
        new_rating = ProductRating(
            pr_user_id=user.get("user_id"),
            pr_product_id=product_id,
            pr_rating=rating
        )
        db.add(new_rating)

    db.commit()
    return {"message": "Product rating added"}
# Get product ratings
@cart_router.get("/get_product_ratings/{product_id}")
def get_product_ratings(product_id: int,
                        db: Session = Depends(get_db)):
    product = db.query(SellProduct).filter(SellProduct.s_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ratings = db.query(ProductRating).filter(ProductRating.pr_product_id == product_id).all()
    total_ratings = len(ratings)
    average_rating = sum(rating.pr_rating for rating in ratings) / total_ratings if total_ratings > 0 else 0

    return {
        "product_id": product.s_id,
        "product_name": product.s_name,
        "total_ratings": total_ratings,
        "average_rating": average_rating
    }

# Filter products by price range
@cart_router.get("/filter_by_price")
def filter_products_by_price(min_price: float = Query(..., title="Minimum Price"),
                             max_price: float = Query(..., title="Maximum Price"),
                             db: Session = Depends(get_db)):
    products = db.query(SellProduct).filter(SellProduct.s_price >= min_price, SellProduct.s_price <= max_price).all()

    filtered_products = [{
        "product_id": product.s_id,
        "product_name": product.s_name,
        "product_price": product.s_price
    } for product in products]

    return filtered_products
"""
@cart_router.get("/filter_by_category")
def filter_products_by_category(category: str = Query(..., title="Category"),
                                db: Session = Depends(get_db)):
    products = db.query(SellProduct).join(ProductCategory).filter(ProductCategory.name == category).all()

    filtered_products = [{
        "product_id": product.s_id,
        "product_name": product.s_name,
        "product_price": product.s_price
    } for product in products]

    return filtered_products
"""