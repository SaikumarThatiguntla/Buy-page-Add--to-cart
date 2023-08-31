from fastapi import FastAPI,Depends,status,HTTPException,Query
from database import engine
from routers import auth, users, cart,wishlist
from database import SessionLocal
from sqlalchemy.orm import session
from models import SellProduct
from fastapi.staticfiles import StaticFiles
import models

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



UPLOAD_FOLDER = "images/sell"
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/images", StaticFiles(directory=UPLOAD_FOLDER), name="images")

app.include_router(auth.router)
app.include_router(cart.cart_router)
app.include_router(wishlist.wishlist_router)
app.include_router(users.router)


# @app.get("/listed_products")
# async def listed_products(db: session = Depends(get_db)):
#     return db.query(Products).all()








