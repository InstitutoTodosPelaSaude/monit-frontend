from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, model_serializer
from typing import Tuple, Any
import hashlib
import secrets

from app.crud.query import SQLGeneratedResponse

class Chat(BaseModel):

    id: str | None = Field(default=None, serialization_alias="_id")
    user_id: str
    name: str
    messages: list[Any] = Field(default_factory=list)

    @model_validator(mode='after')
    def create_id(self):
        self.id = hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()
        return self
    
    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        dict_repr["type"] = "CHAT"
        return dict_repr

class UserMessage(BaseModel):
    message: str
    author: str = "USER"
    type: str = "MESSAGE"
    created_at: datetime = Field(default_factory=datetime.now)

class ChatBotMessage(BaseModel):
    message: str

    generated_query: SQLGeneratedResponse

    author: str = "BOT"
    type: str = "MESSAGE"
    created_at: datetime = Field(default_factory=datetime.now)
