from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=120)

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str | None
    is_active: bool
