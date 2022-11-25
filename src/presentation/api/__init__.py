from fastapi import APIRouter

from .authorization import auth_router

router = APIRouter()
router.include_router(auth_router)
