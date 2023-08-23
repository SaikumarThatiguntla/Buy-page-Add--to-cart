from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel
from .validations import CreateUser
from typing import Optional
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
#to verifying password ,bearer is authorization token and authorization platform
from datetime import datetime, timedelta
from jose import jwt, JWTError



SECRET_KEY = "jikldkaoijeofijaepeo897hjk8"
ALGORITHM = "HS256"



models.Base.metadata.create_all(bind=engine)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
def get_password_hash(password):
    return bcrypt_context.hash(password)
def verify_password(plain_password,hashed_password):
    return bcrypt_context.verify(plain_password,hashed_password)


def authenticate_user(username: str, password: str, db):


    user = db.query(models.User)\
        .filter(models.User.username == username)\
        .first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):
    encode = {"user": username, "user_id": user_id}
    if expires_delta:
        expire = datetime.utcnow()+expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        user_id: int = payload.get("user_id")
        if user_id is None or username is None:
            raise get_user_exception()
        return {'username': username, 'user_id': user_id}
    except:
        raise get_user_exception()


@router.post("/create/user")
def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.User()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.hashed_password = get_password_hash(create_user.password)
    create_user_model.is_active = True
    db.add(create_user_model)
    db.commit()
@router.post("/token")
def login_for_access_token(form_data : OAuth2PasswordRequestForm = Depends(),
                            db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password,db)
    if not user:
        raise token_exception()
    token_expires = timedelta(40)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    return {"access_token": token, "token_type":"Bearer"}

#Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        details = "Could not validate credentials",
        headers = {"WWW-Authenticate" : "Bearer"}
        )
    return credentials_exception
def token_exception():
    token_exception_reponse = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}

    )
    return token_exception_reponse






