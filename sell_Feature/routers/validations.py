from pydantic import BaseModel
from fastapi import Form
from typing import Optional,Union



class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    
class Sell_product(BaseModel):

    title : str
    description: Union[str, None] = None
    category: str
    images:str
    duration: int
    price: int
    location: str

    product_owner_id: int

class Sell_product_form(BaseModel):

    title : str
    description: str
    category: str
    images:Optional[str]
    duration: int
    price:int
    location: str
    # product_owner_id: int

    @classmethod
    def as_form(cls,
                 title: str = Form(...),
                description: str = Form(...),
                category: str = Form(...),
                images: Optional[str] = Form(...),
                duration: int = Form(...),
                price: int = Form(...),
                location: str = Form(...),
                )-> 'Sell_product_form':
        return cls(title= title, description = description, category = category, images = images,
                   duration = duration,price=price, location= location)

