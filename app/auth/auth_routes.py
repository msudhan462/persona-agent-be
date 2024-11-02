# auth_routes.py
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.models.users import User, UserCreate
from app.auth.jwt_handler import create_access_token
from datetime import timedelta
from app.db.mongo import mongo_db
from uuid import uuid4


router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_salt():
    return str(uuid4())


@router.post("/signup")
async def signup(user: UserCreate):

    filters = {
        "email":user.email
    }

    is_user_exist = mongo_db.find(db="auth",collection="users", filters=filters, projection={"_id":0})

    if is_user_exist:
        raise HTTPException(status_code=400, detail="Username already registered")
    

    salt = get_salt()
    hashed_password = get_password_hash(user.password+salt)
    record = {
        "salt":salt,
        "password":hashed_password,
        "email":user.email
    }
    
    status = mongo_db.insert(db="auth",collection="users", records=record)
    print(status)
    return {"message": "User created successfully"}

@router.post("/login")
async def login(user: User):
    
    filters = {
        "email":user.email
    }
    is_user_exist = mongo_db.find(db="auth",collection="users", filters=filters, projection={"_id":0})

    if not is_user_exist:
        raise HTTPException(status_code=400, detail="Username did not registered")
    
    print(is_user_exist)
    hashed_password = is_user_exist['password']
    salt = is_user_exist['salt']
    if not verify_password(user.password+salt, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(hours=12)
    access_token = create_access_token(data={"email": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
