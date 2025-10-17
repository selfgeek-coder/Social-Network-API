from fastapi import FastAPI

from app.routers.auth_router import router as auth_router
from app.routers.posts_router import router as posts_router
from app.database import init_database

init_database()

app = FastAPI(title="Social Network API")

app.include_router(auth_router)
app.include_router(posts_router)