from fastapi import APIRouter

from src.presentation.api.routes.authorization import auth_router

router = APIRouter()
router.include_router(auth_router)
