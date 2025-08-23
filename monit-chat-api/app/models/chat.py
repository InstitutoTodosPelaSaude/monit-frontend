from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, model_serializer, AliasChoices
from typing import Tuple, Any, Literal
import hashlib

from app.models.query import  SQLQuery

# =======================
# TABLE MODELS
# =======================

NEW_CHAT_DEFAULT_NAME = "NEW-CHAT"

class TableColumn(BaseModel):
    name: str
    type: str
    description: str

class TableDatabaseMetadata(BaseModel):
    name: str
    schema: str
    database: str

class Table(BaseModel):

    id: str | None = Field(default=None, serialization_alias="_id")
    name: str
    description: str
    columns: list[TableColumn]
    observations: str | None = None
    type: Literal["TABLE"] = "TABLE"

    metadata: TableDatabaseMetadata

    @model_validator(mode='after')
    def create_id(self):
        self.id = self.name
        return self
    
    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        return dict_repr
    
    @property
    def json_data_dictionary(self):
        data = self.dict()
        del data['metadata']
        return data
    
class UserMessage(BaseModel):
    message: str
    author: str = "USER"
    type: Literal["MESSAGE"] = "MESSAGE"
    created_at: datetime = Field(default_factory=datetime.now)

class ChatBotMessage(BaseModel):
    message: str
    author: str = "BOT"
    type: Literal["MESSAGE"] = "MESSAGE"
    created_at: datetime = Field(default_factory=datetime.now)

    generated_query: SQLQuery
    tables_used_in_query: list[Table] | None = None
    postprocessed_query: str | None = None

class Chat(BaseModel):

    id: str | None = Field(default=None, serialization_alias="_id", validation_alias=AliasChoices('id', '_id'))
    user_id: str
    name: str = Field(default=NEW_CHAT_DEFAULT_NAME)
    messages: list[UserMessage | ChatBotMessage] = Field(default_factory=list)
    type: Literal["CHAT"] = "CHAT"

    @model_validator(mode='after')
    def create_id(self):
        if not self.id:
            self.id = hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()
        return self
    
    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        return dict_repr
    
    def format_to_openai_chat_completion_input(self):

        return [
            {
                'role': 'assistant' if message.author == 'BOT' else 'user' , 
                'content': message.message
            }
            for message 
            in self.messages
        ]
