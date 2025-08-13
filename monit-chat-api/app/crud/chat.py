from app.models.chat import Chat, UserMessage, ChatBotMessage, Table
from app.schemas.chat import TableCreate

from app.crud.database import MongoConnection
from app.crud.exceptions import ChatIDNotFound, TableAlreadyExists
from app.crud.users import read_user_by_id

# from app.services.chat_flow import trigger_chatbot_response_flow

from pymongo.errors import DuplicateKeyError

from datetime import datetime
import hashlib

async def create_chat(user_id):
    db = MongoConnection.get_client()
    db_collection = db.chat
    
    user = await read_user_by_id(user_id)
    new_chat = Chat(user_id=user.id)
    
    db_collection.insert_one(new_chat.dict())

    return new_chat

async def create_bot_reply_message(chat_id: str, message: ChatBotMessage) -> ChatBotMessage:
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat = await read_chat_by_id(chat_id)

    db_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": message.model_dump()}}
    )

    return message

async def create_user_message(chat_id, message="<message>"):
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat = await read_chat_by_id(chat_id)

    new_msg = UserMessage(message=message)

    db_collection.update_one(
        {"_id": chat_id},
        {"$push": {"messages": new_msg.dict()}}
    )

    return new_msg.dict()

async def read_chat_by_id(chat_id):
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat = db_collection.find_one({"_id": chat_id})
    if chat:
        chat = Chat(**chat)
        return chat
    
    raise ChatIDNotFound(chat_id)

async def update_chat_name(chat_id: str, new_name: str):
    db = MongoConnection.get_client()
    db_collection = db.chat

    chat = await read_chat_by_id(chat_id)

    result = db_collection.update_one(
        {"_id": chat_id},
        {"$set": {"name": new_name}}
    )

    if result.modified_count == 0:
        return Chat(**chat)

    updated_chat = await read_chat_by_id(chat_id)
    return Chat(**updated_chat)

async def create_table(payload: TableCreate) -> Table:
    db = MongoConnection.get_client()
    db_collection = db.chat

    new_table = Table(**payload.model_dump())

    try:
        db_collection.insert_one(new_table.dict())
    except DuplicateKeyError as e:
        raise TableAlreadyExists(payload.name)

    return new_table

async def list_tables() -> list[Table]:
    db = MongoConnection.get_client()
    db_collection = db.chat

    docs = db_collection.find({'type': 'TABLE'})
    return [Table(**doc) for doc in docs]