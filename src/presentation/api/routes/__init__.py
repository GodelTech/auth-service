from fastapi import APIRouter

from src.presentation.api.routes.authorization import auth_router
from src.presentation.api.routes.userinfo import userinfo_router
from src.presentation.api.routes.endsession import endsession_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(userinfo_router)

router.include_router(endsession_router)
