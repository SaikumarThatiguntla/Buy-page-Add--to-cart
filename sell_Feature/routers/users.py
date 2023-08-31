from fastapi import APIRouter,Depends,status, Request,HTTPException,Form,status,File,UploadFile
from sqlalchemy.orm import session
from fastapi import FastAPI,Depends,status,HTTPException,Query

from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import  User,SellProduct
import models
from .auth  import get_current_user
from typing import List
import os
from datetime import datetime
import pytz


models.Base.metadata.create_all(bind=engine)


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
async def post_product(title : str =Form(...),
    description: str =Form(...),
    category: str =Form(...),
    duration: int =Form(...),
    price: int =Form(...),
    location: str =Form(...),
                       user: dict = Depends(get_current_user),
                       db: session = Depends(get_db),
                       image_files : List[UploadFile] = File(...)):
    try:

        UPLOAD_FOLDER="images/sell/"+str(user['user_id'])
        #exchange_product = json.loads(exchange_product)
        sell_product_model = models.SellProduct()
        sell_product_model.title = title
        sell_product_model.category = category
        sell_product_model.duration = duration
        sell_product_model.location = location
        sell_product_model.price = price
        #sell_product_model.images = product_to_post.images
        sell_product_model.description = description
        asia_kolkata = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(asia_kolkata)
        sell_product_model.time = current_time
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


@router.get("/products/all/old_to_new")
def get_all_products_old_to_new(db: Session = Depends(get_db)):
    try:
        query = (
            db.query(SellProduct)
            .order_by(SellProduct.time.asc())  # Order by add time in ascending order
            .all()
        )
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No products found"
            )

        return {"message": "successful", "data": query, "status": status.HTTP_200_OK}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@router.get("/products/all/new_to_old")
def get_all_products_new_to_old(db: Session = Depends(get_db)):
    try:
        query = (
            db.query(SellProduct)
            .order_by(SellProduct.time.desc())  # Order by add time in descending order
            .all()
        )
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No products found"
            )

        return {"message": "successful", "data": query, "status": status.HTTP_200_OK}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
@router.get("/all_users")
async def all_users(db: session = Depends(get_db)):
    query=db.query(models.User).all()
    if query is None:
        return {"message":"Failed", "status":status.HTTP_404_NOT_FOUND }

    return {"message": "successful", "data": query, "status": status.HTTP_200_OK}


@router.get("/listed_products")
async def listed_products(db: session = Depends(get_db)):
    try:
        query = db.query(SellProduct).all()
        if query is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")

        return {"message": "succesful", "data": query, "status": status.HTTP_200_OK}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/products/loc")
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

#db.commit()

"""
class Sell_Product_validation(BaseModel):
    s_name: str
    s_category: str
    s_description: str
    s_price : float
    s_owner_id: int

"""



# ...








    


   



    