from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.users import router as users_router
from app.routes.chat import router as chat_router

app = FastAPI(
    title="Monit API",
    version="1.0.0"
)

 # CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 # Routes
app.include_router(users_router, tags=["users"])
app.include_router(chat_router, tags=["chats"])
