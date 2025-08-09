from typing import List, Optional
from beanie import PydanticObjectId
from app.models.user import User
from app.schemas.users import UserCreate

async def create_user(payload: UserCreate) -> User:
    user = User(email=payload.email, name=payload.name)
    return await user.insert()

async def get_user_by_id(user_id: str) -> Optional[User]:
    return await User.get(PydanticObjectId(user_id))

async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one(User.email == email)

async def list_users(limit: int = 50, skip: int = 0) -> List[User]:
    return await User.find().skip(skip).limit(limit).to_list()

async def delete_user(user_id: str) -> bool:
    user = await get_user_by_id(user_id)
    if not user:
        return False
    await user.delete()
    return True
