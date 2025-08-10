from typing import List, Optional
from app.models.user import User
from app.schemas.users import UserCreate

from app.crud.database import MongoConnection
from app.crud.exceptions import UserAlreadyExists

from pymongo.errors import DuplicateKeyError

async def create_user(payload: UserCreate) -> User:
    user = User(email=payload.email, name=payload.name)

    db = MongoConnection.get_client()
    db_collection = db.users

    try:
        db_collection.insert_one(user.dict())
    except DuplicateKeyError as e:
        raise UserAlreadyExists(payload.email)


async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one(User.email == email)

async def list_users(limit: int = 50, skip: int = 0) -> List[User]:
    return await User.find().skip(skip).limit(limit).to_list()
