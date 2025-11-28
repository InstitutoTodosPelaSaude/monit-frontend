from fastapi import APIRouter, HTTPException, Query, status, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.schemas.users import UserCreate, UserOut, Token
from app.models.user import User
from app.crud.users import (
    create_user, 
    list_users, 
    authenticate_user, 
    create_access_token, 
    get_current_user_from_jwt_token
)
from typing import Annotated

from app.crud.exceptions import UserAlreadyExists, UserIDNotFound, UserIDNotFoundOrInvalidPassword

router = APIRouter(prefix="/user", tags=["users"])
auth_router = APIRouter(tags=["users"])

@router.post("", response_model=UserOut, status_code=201, summary="Cria usuário")
async def create_user_route(payload: UserCreate):
    
    try:
        await create_user(payload)
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # Erro genérico não esperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return UserOut(email=payload.email, name=payload.name)

@router.get("", response_model=list[UserOut], summary="Lista usuários")
async def list_users_route( current_user: Annotated[User, Depends(get_current_user_from_jwt_token)] ):
    docs = await list_users()
    return [UserOut(id=str(d.id), email=d.email, name=d.name, is_active=d.is_active) for d in docs]

@router.get("/me/", response_model=UserOut, summary="")
async def list_users_me_route(
    current_user: Annotated[User, Depends(get_current_user_from_jwt_token)]
):
    """
    Retorna o usuário autenticado.
    """
    return UserOut(
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        favorite_queries_ids=current_user.favorite_queries_ids
    )

@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    
    try:
        user = await authenticate_user(form_data.username, form_data.password)
    except (UserIDNotFound, UserIDNotFoundOrInvalidPassword):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id})

    return Token(access_token=access_token, token_type="bearer")
