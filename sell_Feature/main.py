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

@app.get("/all_users")
async def all_users(db: session = Depends(get_db)):
    query=db.query(models.User).all()
    if query is None:
        return {"message":"Failed", "status":status.HTTP_404_NOT_FOUND }

    return {"message": "successful", "data": query, "status": status.HTTP_200_OK}


@app.get("/listed_products")
async def listed_products(db: session = Depends(get_db)):
    try:
        query = db.query(SellProduct).all()
        if query is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")

        return {"message": "succesful", "data": query, "status": status.HTTP_200_OK}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/products/loc")
async def get_products(location: str = Query(None, description="Location"),
                       category: str = Query(None, description="Category")):
    try:
        db = SessionLocal()
        query = db.query(SellProduct)

        if location:
            query = query.filter(SellProduct.location == location)

        if category:
            query = query.filter(SellProduct.category == category)

        filtered_products = query.all()
        db.close()
        if query is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
        return {"message": "successful", "data": filtered_products, "status": status.HTTP_200_OK}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# @app.get("/listed_products")
# async def listed_products(db: session = Depends(get_db)):
#     return db.query(Products).all()








