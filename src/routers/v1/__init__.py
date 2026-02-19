from fastapi import APIRouter

from .books import books_router

# from .users import users_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])

v1_router.include_router(books_router)
# v1_router.include_router(users_router)
