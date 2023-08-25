from fastapi import APIRouter,Depends,status, Request,HTTPException,status,File,UploadFile
from sqlalchemy.orm import session
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import  User,SellProduct
import models
from .auth  import get_current_user
from typing import List
import os
from .validations import Sell_product_form,Sell_product
models.Base.metadata.create_all(bind=engine)
"""
class Sell_Product_validation(BaseModel):
    s_name: str
    s_category: str
    s_description: str
    s_price : float
    s_owner_id: int

"""


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
    if user is None:
        return {"message":"user not found", "status":status.HTTP_404_NOT_FOUND }

    return {"message": "successful","data":user,"status":status.HTTP_200_OK }

@router.get("/products")
def get_products_post_by_specific_user( user: dict = Depends(get_current_user),db: session = Depends(get_db )):
    try:
        query = db.query(SellProduct)\
            .filter(SellProduct.s_owner_id == user.get("user_id") )\
            .all()
        if query is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")

        return {"message": "successful", "data": query, "status": status.HTTP_200_OK}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.post("/post_product")
async def post_product( product_to_post : Sell_product_form=Depends() ,
                       user: dict = Depends(get_current_user),
                       db: session = Depends(get_db),image_files:List[UploadFile]=File(...)):
    try:

        UPLOAD_FOLDER="images/sell/"+str(user['user_id'])
        #exchange_product = json.loads(exchange_product)
        sell_product_model = models.SellProduct()
        sell_product_model.title = product_to_post.title
        sell_product_model.category = product_to_post.category
        sell_product_model.duration = product_to_post.duration
        sell_product_model.location = product_to_post.location
        sell_product_model.price = product_to_post.price
        sell_product_model.images = product_to_post.images
        sell_product_model.description = product_to_post.description
        sell_product_model.s_owner_id = user.get("user_id")
        """
        category_name = product_to_post.category
        category = db.query(ProductCategory).filter(ProductCategory.name == category_name).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category name")

        sell_product_model.category = category.id
        """
        db.add(sell_product_model)
        print(sell_product_model)
        db.commit()

        product_folder_path = os.path.join(UPLOAD_FOLDER, str(sell_product_model.id))
        os.makedirs(product_folder_path, exist_ok=True)
        saved_image_paths = []
        # Save uploaded images to the product's folder
        for image in image_files:
            image_path = os.path.join(product_folder_path, image.filename)
            with open(image_path, "wb") as image_file:
                image_file.write(image.file.read())
            saved_image_paths.append(image_path)
        # exchange_product_model.images = saved_image_paths
        sell_product_model.images = product_folder_path  # storing the path

        db.commit()
        # Save the image path to the database
        # return exchange_product_model
        return {"message": "product posted ", "status_code": status.HTTP_201_CREATED}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/delete_product/{product_id}")
async def delete_product(product_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        product = db.query(SellProduct).filter(
            SellProduct.id == product_id, SellProduct.s_owner_id == user.get("user_id")).first()

        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        # Delete the images associated with the product (you might want to add this logic)
        # ...

        db.delete(product)
        db.commit()

        return {"message": "Product deleted successfully", "status_code": status.HTTP_200_OK}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



#     db.commit()




# ...








    


   



    