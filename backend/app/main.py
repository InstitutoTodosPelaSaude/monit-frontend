from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import lifespan

from .routes.health import router as health_router
from .routes.users import router as users_router

app = FastAPI(
    title="Monit API",
    version="1.0.0",
    lifespan=lifespan,
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
app.include_router(health_router, tags=["health"])
app.include_router(users_router, tags=["users"])

