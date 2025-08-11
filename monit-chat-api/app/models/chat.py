from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, model_serializer
from typing import Tuple, Any, Literal
import hashlib
import secrets

from app.models.query import SQLGeneratedResponse

class Chat(BaseModel):

    id: str | None = Field(default=None, serialization_alias="_id")
    user_id: str
    name: str
    messages: list[Any] = Field(default_factory=list)
    type: Literal["CHAT"] = "CHAT"

    @model_validator(mode='after')
    def create_id(self):
        self.id = hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()
        return self
    
    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        return dict_repr

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

    generated_query: SQLGeneratedResponse

# =======================
# TABLE MODELS
# =======================

class TableColumn(BaseModel):
    name: str
    type: str
    description: str

class TableMetadata(BaseModel):
    name: str
    schema: str
    database: str

class Table(BaseModel):

    id: str | None = Field(default=None, serialization_alias="_id")
    name: str
    description: str
    columns: list[TableColumn]
    observations: list[str]
    type: Literal["TABLE"] = "TABLE"

    metadata: TableMetadata

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
