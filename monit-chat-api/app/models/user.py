from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, model_serializer
from typing import Tuple, Any

class User(BaseModel):
    id: str | None = Field(default=None, serialization_alias="_id")
    
    email: EmailStr
    name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='after')
    def create_id(self):
        self.id = self.email

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        dict_repr = dict(self)
        dict_repr['_id'] = dict_repr['id']
        del dict_repr['id']
        return dict_repr

if __name__ == "__main__":

    _user = User(email="joaopedro@gmail.com", name="oi")
    print(_user.dict())