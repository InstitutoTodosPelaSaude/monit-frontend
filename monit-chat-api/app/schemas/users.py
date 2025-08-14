from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=120)
    password: str

class UserOut(BaseModel):
    email: EmailStr
    name: str | None
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str