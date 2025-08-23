from app.models.chat import Chat, UserMessage, ChatBotMessage, Table
from app.schemas.chat import TableCreate, ChatBasicIdentifiers, TableUpdate

from app.crud.database import MongoConnection
from app.crud.exceptions import ChatIDNotFound, TableAlreadyExists, TableIDNotFound
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
    return updated_chat

async def list_chat_ids_and_names_by_user_id(user_id: str) -> list[ChatBasicIdentifiers]:
    db = MongoConnection.get_client()
    db_collection = db.chat

    chats = db_collection.find(
        {"user_id": user_id, "type": "CHAT"}, 
        {"_id": 1, "name": 1,}
    )
    return [
        ChatBasicIdentifiers(
            chat_id=str(chat["_id"]),
            name=chat["name"]
        ) for chat in chats
    ]

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

async def read_table_by_id(table_id: str) -> Table:
    db = MongoConnection.get_client()
    db_collection = db.chat

    table = db_collection.find_one({'_id': table_id, 'type': 'TABLE'})
    if table:
        return Table(**table)

    raise TableIDNotFound(table_id)

async def update_table(payload: TableUpdate) -> Table:
    db = MongoConnection.get_client()
    db_collection = db.chat

    table_id = payload.name
    original_table = await read_table_by_id(table_id)

    original_table.description = payload.description or original_table.description
    original_table.observations = payload.observations or original_table.observations
    
    columns_in_update_payload = {col.name: col for col in payload.columns}
    for col in original_table.columns:
        if col.name in columns_in_update_payload:
            col.description = columns_in_update_payload[col.name].description or col.description
    
    db_collection.update_one({"_id": table_id}, {"$set": original_table.dict()})
    
    updated_table = await read_table_by_id(table_id)
    return Table(**updated_table.dict())