from fastapi import APIRouter, HTTPException, Query
from app.schemas.users import UserCreate, UserOut
from app.crud.users import create_user, get_user_by_email, list_users, delete_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=201, summary="Cria usuário")
async def create_user_route(payload: UserCreate):
    exists = await get_user_by_email(payload.email)
    if exists:
        raise HTTPException(status_code=409, detail="email já cadastrado")
    doc = await create_user(payload)
    return UserOut(id=str(doc.id), email=doc.email, name=doc.name, is_active=doc.is_active)

@router.get("", response_model=list[UserOut], summary="Lista usuários")
async def list_users_route(limit: int = Query(50, le=200), skip: int = 0):
    docs = await list_users(limit=limit, skip=skip)
    return [UserOut(id=str(d.id), email=d.email, name=d.name, is_active=d.is_active) for d in docs]

@router.delete("/{user_id}", status_code=204, summary="Remove usuário")
async def delete_user_route(user_id: str):
    ok = await delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="usuário não encontrado")
    return
