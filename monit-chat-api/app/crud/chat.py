from app.models.chat import Chat, UserMessage, ChatBotMessage

from app.crud.database import MongoConnection
from app.crud.exceptions import ChatIDNotFound
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

async def create_bot_reply_message(chat_id: str, user_message: str) -> ChatBotMessage:
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat = await read_chat_by_id(chat_id)

    # [WIP] Create AI response logic
    message = user_message
    sql_generated = "SELECT * FROM TESTE"
    
    new_msg = ChatBotMessage(message=user_message, sql_generated=sql_generated)
    db_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": new_msg.model_dump()}}
    )

    return new_msg

async def create_user_message(chat_id, message="<message>"):
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat = await read_chat_by_id(chat_id)

    new_msg = UserMessage(message=message)

    db_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": new_msg.dict()}}
    )

    await create_bot_reply_message(chat_id, message)

    return new_msg.dict()

async def read_chat_by_id(chat_id):
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat_data = db_collection.find_one({"_id": chat_id})
    if chat_data:
        return Chat(**chat_data)
    
    raise ChatIDNotFound(chat_id)