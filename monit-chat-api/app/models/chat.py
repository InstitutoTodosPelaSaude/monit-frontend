from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, model_serializer
from typing import Tuple, Any
import hashlib
import secrets


class Chat(BaseModel):

    id: str | None = Field(default=None, serialization_alias="_id")
    user_id: str
    name: str
    messages: list[str] = Field(default_factory=list)

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
