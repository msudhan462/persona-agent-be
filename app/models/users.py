# models/user.py
from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str

class UserCreate(User):
    email: str
    password: str
    name: str

class UserInDB(User):
    hashed_password: str
