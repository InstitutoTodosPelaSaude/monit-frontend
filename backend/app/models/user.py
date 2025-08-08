from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field, EmailStr


class User(Document):
    email: Indexed(EmailStr, unique=True)  # índice único
    name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"  # nome da coleção

    async def before_replace(self):
        # atualiza updated_at em updates substitutivos
        self.updated_at = datetime.now()
