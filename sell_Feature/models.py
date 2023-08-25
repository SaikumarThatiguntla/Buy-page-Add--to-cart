from sqlalchemy import Column, Integer, String,ForeignKey,Float
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    s_products = relationship("SellProduct", back_populates="s_owner")
    s_carts = relationship("SellCart", back_populates="s_user")
    rated_products = relationship("ProductRating", back_populates="pr_user")


class SellProduct(Base):
    __tablename__ = "sellproducts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    category= Column(String)
    description = Column(String)
    price = Column(Float)
    images = Column(String)
    duration = Column(Integer)
    location = Column(String)
    s_owner_id = Column(Integer, ForeignKey("users.id"))
    
    s_owner = relationship("User", back_populates="s_products")
    s_carts = relationship("SellCart", back_populates="s_product")
    product_ratings = relationship("ProductRating", back_populates="pr_product")
    #category_id = Column(Integer, ForeignKey("productcategories.id"))
    #category = relationship("ProductCategory", back_populates="products")

class SellCart(Base):
    __tablename__ = "sellcarts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("sellproducts.id"))
    quantity = Column(Integer)
    
    s_user = relationship("User", back_populates="s_carts")
    s_product = relationship("SellProduct", back_populates="s_carts")
    #s_payment = relationship("SellPayment", uselist=False, back_populates="s_carts")
    #uselist = False indicates a one-to-one or many-to-one relationship,
    #  where the relationship returns a single object.
    #  For example, each cart has a single associated payment.
"""
class SellPayment(Base):
    __tablename__ = "sellpayments"

    id = Column(Integer, primary_key=True, index=True)
    s_cart_id = Column(Integer, ForeignKey("sellcarts.id"))
    s_payment_method = Column(String)
    s_payment_status = Column(String)
    
    s_cart = relationship("SellCart", back_populates="s_payment")
"""

class ProductRating(Base):
    __tablename__ = "productratings"

    pr_id = Column(Integer, primary_key=True, index=True)
    pr_user_id = Column(Integer, ForeignKey("users.id"))
    pr_product_id = Column(Integer, ForeignKey("sellproducts.id"))
    pr_rating = Column(Integer)

    pr_user = relationship("User", back_populates="rated_products")
    pr_product = relationship("SellProduct", back_populates="product_ratings")

"""
class ProductCategory(Base):
    __tablename__ = "productcategories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    products = relationship("SellProduct", back_populates="category")

class ProductPrice(Base):
    __tablename__ = "productprices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("sellproducts.s_id"))
    price = Column(Float)
    date_added = Column(DateTime, default=datetime.utcnow)

    product = relationship("SellProduct", back_populates="prices")
"""