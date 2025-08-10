from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Tuple

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


if __name__ == "__main__":

    _user = User(email="joaopedro@gmail.com", name="oi")
    print(_user.model_dump(by_alias=True))