# auth_routes.py
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from app.models.users import User, UserCreate
from app.auth.jwt_handler import create_access_token
from datetime import timedelta
from app.db.mongo import mongo_db
from uuid import uuid4
import traceback


router = APIRouter(prefix="/api/auth")

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
        return {"status_code": 409, "message" : "email already registered", "error":True}
    

    salt = get_salt()
    hashed_password = get_password_hash(user.password+salt)
    persona_id = str(user.name).strip().replace(" ","_")
    record = {
        "salt":salt,
        "password":hashed_password,
        "email":user.email,
        "persona_id":persona_id
    }
    
    status = mongo_db.insert(db="auth",collection="users", records=record)
    print(status)

    access_token_expires = timedelta(hours=12)
    access_token = create_access_token(data={"email": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
async def login(user: User):
    
    filters = {
        "email":user.email
    }
    is_user_exist = mongo_db.find(db="auth",collection="users", filters=filters, projection={"_id":0})

    if not is_user_exist:
        return {"status_code": 404, "message" : "Username did not registered", "error":True}
    
    print(is_user_exist)
    hashed_password = is_user_exist['password']
    salt = is_user_exist['salt']
    if not verify_password(user.password+salt, hashed_password):
        return {"status_code": 401, "message" : "Invalid credentials", "error":True}

    access_token_expires = timedelta(hours=12)
    access_token = create_access_token(data={"email": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
