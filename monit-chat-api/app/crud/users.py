from typing import List, Optional
from app.models.user import User
from app.schemas.users import UserCreate

from app.crud.database import MongoConnection
from app.crud.exceptions import UserAlreadyExists

from pymongo.errors import DuplicateKeyError

async def create_user(payload: UserCreate) -> User:
    user = User(email=payload.email, name=payload.name, password=payload.password)

    db = MongoConnection.get_client()
    db_collection = db.users

    try:
        db_collection.insert_one(user.dict())
    except DuplicateKeyError as e:
        raise UserAlreadyExists(payload.email)

async def list_users() -> List[User]:
    db = MongoConnection.get_client()
    db_collection = db.users

    query_result = db_collection.find({'is_active': True})

    users = [User(**doc) for doc in list(query_result)]
    
    return users