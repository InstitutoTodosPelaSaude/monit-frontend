from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, model_serializer
from typing import Tuple, Any
import hashlib
import secrets

class User(BaseModel):
    id: str | None = Field(default=None, serialization_alias="_id")
    
    email: EmailStr
    name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    password: str
    password_salt: str | None = None

    @model_validator(mode='after')
    def create_id(self):
        self.id = self.email
        return self

    @model_validator(mode='after')
    def encrypt_password(self):
        salt = secrets.token_hex(16)
        hash_ = hashlib.sha256((self.password + salt).encode()).hexdigest()

        self.password_salt = salt
        self.password = hash_
        return self

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        return dict_repr

if __name__ == "__main__":

    _user = User(email="joaopedro@gmail.com", name="oi", password="teste123")
    print(_user.dict())