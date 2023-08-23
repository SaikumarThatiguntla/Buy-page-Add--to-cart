from fastapi import FastAPI,Depends
from database import engine
from routers import auth, users, cart
from database import SessionLocal
from sqlalchemy.orm import session
import models

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




app = FastAPI()

models.Base.metadata.create_all(bind=engine)



app.include_router(auth.router)
app.include_router(cart.cart_router)

app.include_router(users.router)

@app.get("/all_users")
async def all_users(db: session = Depends(get_db)):
    return db.query(models.User).all()


# @app.get("/listed_products")
# async def listed_products(db: session = Depends(get_db)):
#     return db.query(Products).all()








