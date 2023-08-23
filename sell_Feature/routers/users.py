from fastapi import APIRouter,Depends, Request,HTTPException
from sqlalchemy.orm import session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import  User,SellProduct
import models
from .auth  import get_current_user

models.Base.metadata.create_all(bind=engine)

class Sell_Product_validation(BaseModel):
    s_name: str
    s_category: str
    s_description: str
    s_price : float
    s_owner_id: int




router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={401: {"user": "Not authorized"}}
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/")
async def logined_user(user: dict = Depends(get_current_user)):

    return user

@router.get("/products")
def get_products_post_by_specific_user( user: dict = Depends(get_current_user),db: session = Depends(get_db )):
    query = db.query(SellProduct)\
        .filter(SellProduct.s_owner_id == user.get("user_id") )\
        .all()
    return query

@router.post("/post_product")
async def post_product( product_to_post : Sell_Product_validation ,
                       user: dict = Depends(get_current_user),
                       db: session = Depends(get_db)):
    print(user)
    sell_product_model = models.SellProduct()
    sell_product_model.s_name = product_to_post.s_name
    sell_product_model.s_category = product_to_post.s_category
    sell_product_model.s_price = product_to_post.s_price
    sell_product_model.s_description = product_to_post.s_description
    sell_product_model.s_owner_id = user.get("user_id")
   
    
    db.add(sell_product_model)
    print(sell_product_model)
    db.commit()
    return "done"



#     db.commit()




# ...








    


   



    