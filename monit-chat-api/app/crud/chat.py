from typing import List, Optional
from app.models.user import User
from app.models.chat import Chat
from app.schemas.users import UserCreate

from app.crud.database import MongoConnection
from app.crud.exceptions import UserAlreadyExists, UserIDNotFound
from app.crud.users import read_user_by_id

from datetime import datetime
import hashlib

async def create_chat(user_id, name="<chat>"):
    db = MongoConnection.get_client()
    db_collection = db.chat
    
    user = await read_user_by_id(user_id)
    new_chat = Chat(user_id=user.id, name=name)
    
    db_collection.insert_one(new_chat.dict())

    return new_chat