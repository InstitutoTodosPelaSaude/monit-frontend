from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field, EmailStr


class User(Document):
    email: Indexed(EmailStr, unique=True)  # unique index
    name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"  # collection name

    async def before_replace(self):
        # updates updated_at in replacement updates
        self.updated_at = datetime.now()
