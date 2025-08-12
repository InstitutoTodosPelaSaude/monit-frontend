from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.chat import TableCreate
from app.crud.chat import create_chat, create_user_message, read_chat_by_id, create_table, list_tables

from app.crud.exceptions import UserIDNotFound, ChatIDNotFound, TableAlreadyExists
from app.services.chat_flow import trigger_chatbot_response_flow

router = APIRouter(prefix="/chat")

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

@router.post("/message", summary="Cria uma mensagem em um chat", status_code=status.HTTP_201_CREATED)
async def create_chat_message_route(
    chat_id: str = Query(..., description="ID do usuário para associar ao chat"),
    message: str = Query(..., description="Mensagem"),
):
    
    try:
        message = await create_user_message(chat_id, message)
        await trigger_chatbot_response_flow(chat_id, message)
    except ChatIDNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    
    return message

@router.get("/{chat_id}", summary="Busca um chat por ID")
async def get_chat_route(chat_id: str):
    try:
        chat = await read_chat_by_id(chat_id)
        return chat
    except ChatIDNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
@router.post("/table", status_code=status.HTTP_201_CREATED, summary="Cria uma nova tabela")
async def create_table_route(payload: TableCreate):
    try:
        table = await create_table(payload)
        return table
    except TableAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
@router.get("/table/", summary="Lista todas as tabelas cadastradas")
async def list_tables_route():
    docs = await list_tables()
    return docs