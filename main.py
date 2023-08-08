from fastapi import FastAPI,Depends,HTTPException
from database import engine
from models import Product

from database import SessionLocal
from sqlalchemy.orm import session
from pydantic import BaseModel
import models
from typing import List
from sqlalchemy import select
from models import Cart
import schemas
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




app = FastAPI()



models.Base.metadata.create_all(bind=engine)



@app.get("/all_users")
async def all_users(db: session = Depends(get_db)):
    return db.query(models.User).all()


@app.get("/listed_products")
async def listed_products(db: session = Depends(get_db)):
    return db.query(Product).all()



@app.post("/ratings/", response_model=schemas.Rating)
def create_rating(rating: schemas.RatingCreate, db: session = Depends(get_db)):
    db_rating = models.Rating(**rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.get("/carts/{user_id}", response_model=List[schemas.Cart])
def get_user_cart(user_id: int, db: session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_cart = user.carts
    return user_cart