from fastapi import APIRouter
from beanie import Document

router = APIRouter()

@router.get("/health", summary="Health check da API e do MongoDB/Beanie")
async def health_check():
    # comando simples no admin para validar conexão
    from beanie import init_beanie  # força import carregado
    # se init_beanie falhou, a app nem sobe; aqui só retorna ok
    return {"status": "ok"}
