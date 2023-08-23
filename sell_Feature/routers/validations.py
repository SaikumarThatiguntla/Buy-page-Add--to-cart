from pydantic import BaseModel
from typing import Optional



class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    password: str
    
