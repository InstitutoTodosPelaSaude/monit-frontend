from typing import List, Optional, Annotated
from app.models.user import User
from app.models.chat import Chat
from app.schemas.users import UserCreate, Token

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta, timezone

from app.crud.database import MongoConnection
from app.crud.exceptions import (
    UserAlreadyExists, 
    UserIDNotFound, 
    UserIDNotFoundOrInvalidPassword
)

from datetime import datetime
import bcrypt

from pymongo.errors import DuplicateKeyError
import os

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate_user(username, password) -> User:
    db = MongoConnection.get_client()
    db_collection = db.users

    user = await read_user_by_id(username)
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise UserIDNotFoundOrInvalidPassword(username)
    
    return user

async def create_user(payload: UserCreate) -> User:
    
    # Generate hashed password and salt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(payload.password.encode('utf-8'), salt).decode('utf-8')

    new_user = User(
        email=payload.email, 
        name=payload.name, 
        password=hashed_password
    )

    db = MongoConnection.get_client()
    db_collection = db.users

    try:
        db_collection.insert_one(new_user.dict())
    except DuplicateKeyError as e:
        raise UserAlreadyExists(payload.email)

async def list_users() -> List[User]:
    db = MongoConnection.get_client()
    db_collection = db.users

    query_result = db_collection.find({'is_active': True, 'type': 'USER',})

    users = [User(**doc) for doc in list(query_result)]
    
    return users

async def read_user_by_id(id) -> User:
    db = MongoConnection.get_client()
    db_collection = db.users

    query_result = db_collection.find_one(
        {
            '_id': id,
            'type': 'USER',
            'is_active': True
        }
    )

    if not query_result:
        raise UserIDNotFound(id)

    user = User(**query_result)
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_from_jwt_token(token: Annotated[str, Depends(oauth2_scheme)]) -> User:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        username = str(username)
        user = await read_user_by_id(username)
    except (InvalidTokenError, UserIDNotFound) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{str(e)} .Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user