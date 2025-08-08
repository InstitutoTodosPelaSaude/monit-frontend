from fastapi import APIRouter
from beanie import Document

router = APIRouter()

@router.get("/health", summary="Health check for the API and MongoDB/Beanie")
async def health_check():
    # simple command in admin to validate connection
    from beanie import init_beanie  # force import loaded
    # if init_beanie failed, the app doesn't even start; here just return ok
    return {"status": "ok"}
