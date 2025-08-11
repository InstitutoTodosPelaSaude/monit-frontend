from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.users import UserCreate, UserOut
from app.crud.chat import create_chat

from app.crud.exceptions import UserAlreadyExists, UserIDNotFound

router = APIRouter(prefix="/chat", tags=["users"])

@router.post("", summary="Cria um chat para um usuário", status_code=status.HTTP_201_CREATED)
async def create_chat_route(
    user_id: str = Query(..., description="ID do usuário para associar ao chat")
):
    """
    Cria um novo chat vinculado a um usuário existente.
    """
    try:
        chat = await create_chat(user_id)
        return chat

    except UserIDNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar chat."
        )
