from fastapi import APIRouter, HTTPException, Query, status, Depends, Query
from typing import Annotated

from app.schemas.chat import TableCreate
from app.models.user import User
from app.crud.chat import create_chat, create_user_message, read_chat_by_id, create_table, list_tables
from app.crud.users import get_current_user_from_jwt_token
from app.crud.query import read_query_by_id

from app.crud.exceptions import UserIDNotFound, ChatIDNotFound, TableAlreadyExists
from app.crud.exceptions import QueryIDNotFound, QueryCannotBeExecuted

from app.services.chat_flow import trigger_chatbot_response_flow
from app.services.query_execution import trigger_query_execution_flow

router = APIRouter(prefix="/chat")

@router.post("", summary="Cria um chat para um usuário", status_code=status.HTTP_201_CREATED)
async def create_chat_route(
    current_user: Annotated[User, Depends(get_current_user_from_jwt_token)],
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
    current_user: Annotated[User, Depends(get_current_user_from_jwt_token)],
    chat_id: str = Query(..., description="ID do usuário para associar ao chat"),
    message: str = Query(..., description="Mensagem"),
):
    
    try:
        message = await create_user_message(chat_id, message)
        await trigger_chatbot_response_flow(chat_id)
    except ChatIDNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    return message

@router.get("/{chat_id}", summary="Busca um chat por ID")
async def get_chat_route(
    current_user: Annotated[User, Depends(get_current_user_from_jwt_token)],
    chat_id: str
):
    try:
        chat = await read_chat_by_id(chat_id)
        return chat
    except ChatIDNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
@router.post("/table", status_code=status.HTTP_201_CREATED, summary="Cria uma nova tabela")
async def create_table_route(
    current_user: Annotated[User, Depends(get_current_user_from_jwt_token)],
    payload: TableCreate
):
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

@router.get("/query/result", summary="Executa uma consulta e recupera os dados dela.")
async def get_data_from_query(
    current_user: Annotated[User, Depends(get_current_user_from_jwt_token)],
    query_id: str,
    execute_query: bool = Query(True)
):
    try:
        if execute_query:
            await trigger_query_execution_flow(query_id)
        query = await read_query_by_id(query_id)
        return query
    except QueryIDNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except QueryCannotBeExecuted as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
