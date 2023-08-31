from pydantic import BaseModel,Field
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
