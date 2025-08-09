from contextlib import asynccontextmanager
from typing import Sequence
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from beanie import init_beanie

# IMPORT HERE all Document models registered in Beanie
from app.models.user import User

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    MONGO_URI: str  # e.g.: mongodb://appuser:pass@mongodb:27018/appdb?authSource=appdb
    MONGO_DB: str = "appdb"
    APP_ENV: str = "production"  # production | development

settings = Settings()

_motor_client: AsyncIOMotorClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _motor_client
    _motor_client = AsyncIOMotorClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )
    try:
        # validate connection at startup
        await _motor_client[settings.MONGO_DB].command("ping")

        print(f"[startup] Connected to MongoDB")

        # register documents in Beanie + create/update declared indexes
        docs: Sequence[type] = [User]
        await init_beanie(database=_motor_client[settings.MONGO_DB], document_models=docs)
    except Exception as e:
        import sys
        print(f"[startup] Failed to connect/register in MongoDB: {e}", file=sys.stderr)
        print(settings.MONGO_URI)
        raise

    yield

    _motor_client.close()
