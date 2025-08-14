from typing import List, Optional
from app.models.user import User
from app.models.chat import Chat
from app.schemas.users import UserCreate

from app.crud.database import MongoConnection
from app.crud.exceptions import (
    UserAlreadyExists, 
    UserIDNotFound, 
    UserIDNotFoundOrInvalidPassword
)

from datetime import datetime
import bcrypt

from pymongo.errors import DuplicateKeyError

async def authenticate_user(username, password) -> User:
    db = MongoConnection.get_client()
    db_collection = db.users

    user = User(
        **db_collection
        .find_one(
            {
                'is_active': True, 
                'type': 'USER',
                '_id': username
            }
        )
    )
    

    if not user:
        raise UserIDNotFound(username)
    
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