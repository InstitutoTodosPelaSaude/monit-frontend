from contextlib import asynccontextmanager
from typing import Sequence
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from beanie import init_beanie

# IMPORTAR AQUI todos os Document models registrados no Beanie
from .models.user import User

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    MONGO_URI: str  # ex: mongodb://appuser:pass@mongodb:27018/appdb?authSource=appdb
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
        # valida conexão logo na subida
        await _motor_client[settings.MONGO_DB].command("ping")

        print(f"[startup] Conectado ao MongoDB: {settings.MONGO_URI}")

        # registra documentos no Beanie + cria/atualiza índices declarados
        docs: Sequence[type] = [User]
        await init_beanie(database=_motor_client[settings.MONGO_DB], document_models=docs)
    except Exception as e:
        import sys
        print(f"[startup] Falha ao conectar/registrar no MongoDB: {e}", file=sys.stderr)
        raise

    yield

    _motor_client.close()
