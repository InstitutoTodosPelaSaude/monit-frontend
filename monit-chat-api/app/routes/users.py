from fastapi import APIRouter, HTTPException, Query, status, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.schemas.users import UserCreate, UserOut
from app.crud.users import create_user, list_users, authenticate_user
from typing import Annotated

from app.crud.exceptions import UserAlreadyExists, UserIDNotFound, UserIDNotFoundOrInvalidPassword

router = APIRouter(prefix="/user", tags=["users"])

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
async def list_users_route():
    docs = await list_users()
    return [UserOut(id=str(d.id), email=d.email, name=d.name, is_active=d.is_active) for d in docs]

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    try:
        user = await authenticate_user(form_data.username, form_data.password)
    except (UserIDNotFound, UserIDNotFoundOrInvalidPassword):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    
    return {"access_token": user.name, "token_type": "bearer"}
